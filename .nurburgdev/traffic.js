import http from "k6/http";
import { check, sleep } from "k6";
import { Rate } from "k6/metrics";

export let errorRate = new Rate("errors");

export let options = {
  stages: [
    { duration: "15m", target: 20 }, // Stay at 20 users for 1 minute
  ],
};

const BASE_URL = "http://py-inventory-mgmt:8000";

export default function () {
  const params = {
    headers: {
      "Content-Type": "application/json",
      // Add authentication headers if needed:
      // 'Authorization': 'Bearer your-token-here',
    },
  };

  // Test POST /sku

  let response1 = http.post(
    `${BASE_URL}/sku`,
    JSON.stringify({
      sku_code: `SKU-${Math.random().toString(36).substring(2, 8)}`,
      name: "Test Product",
      quantity: 100,
      price: 49.99,
    }),
    params
  );

  // Customize these checks based on your API's expected behavior
  check(response1, {
    "POST /sku status is 200": (r) => r.status === 200,
    "POST /sku response time < 500ms": (r) => r.timings.duration < 500,
    "POST /sku has sku_id": (r) => {
      try {
        return JSON.parse(r.body).hasOwnProperty("sku_id");
      } catch {
        return false;
      }
    },
    "POST /sku has sku_code": (r) => {
      try {
        return JSON.parse(r.body).hasOwnProperty("sku_code");
      } catch {
        return false;
      }
    },
  }) || errorRate.add(1);

  // Extract sku_id from first response for temporary block test
  let skuId = "test-sku-id";
  try {
    if (response1.status === 200) {
      const data = JSON.parse(response1.body);
      skuId = data.sku_id || "test-sku-id";
    }
  } catch {}

  // Test POST /sku/{sku_id}/temporary-block

  let response2 = http.post(
    `${BASE_URL}/sku/${skuId}/temporary-block`,
    JSON.stringify({
      quantity: 5,
      reason: "Load test reservation",
      expires_at: "2024-12-31T23:59:59Z",
    }),
    params
  );

  // Customize these checks based on your API's expected behavior
  check(response2, {
    "POST /sku/{sku_id}/temporary-block status is 200": (r) => r.status === 200,
    "POST /sku/{sku_id}/temporary-block response time < 500ms": (r) =>
      r.timings.duration < 500,
    "POST /sku/{sku_id}/temporary-block has block_id": (r) => {
      try {
        return JSON.parse(r.body).hasOwnProperty("block_id");
      } catch {
        return false;
      }
    },
    "POST /sku/{sku_id}/temporary-block has status": (r) => {
      try {
        return JSON.parse(r.body).hasOwnProperty("status");
      } catch {
        return false;
      }
    },
  }) || errorRate.add(1);

  // Test GET /temporary-blocks

  let response3 = http.get(`${BASE_URL}/temporary-blocks`, params);

  // Customize these checks based on your API's expected behavior
  check(response3, {
    "GET /temporary-blocks status is 200": (r) => r.status === 200,
    "GET /temporary-blocks response time < 500ms": (r) =>
      r.timings.duration < 500,
    "GET /temporary-blocks has blocks array": (r) => {
      try {
        return Array.isArray(JSON.parse(r.body).blocks);
      } catch {
        return false;
      }
    },
    "GET /temporary-blocks has total count": (r) => {
      try {
        return JSON.parse(r.body).hasOwnProperty("total");
      } catch {
        return false;
      }
    },
  }) || errorRate.add(1);

  // Extract block_id from second response for convert test
  let blockId = "test-block-id";
  try {
    if (response2.status === 200) {
      const data = JSON.parse(response2.body);
      blockId = data.block_id || "test-block-id";
    }
  } catch (e) {}

  let response4 = http.post(
    `${BASE_URL}/temporary-blocks/${blockId}/convert-to-permanent`,
    JSON.stringify({
      reason: "Load test order confirmed",
    }),
    params
  );

  // Customize these checks based on your API's expected behavior
  check(response4, {
    "POST /temporary-blocks/{block_id}/convert-to-permanent status is 200": (
      r
    ) => r.status === 200,
    // Adjust expected status code if needed (201 for created, 204 for no content, etc.)
    "POST /temporary-blocks/{block_id}/convert-to-permanent response time < 500ms":
      (r) => r.timings.duration < 500,
  }) || errorRate.add(1);

  // Test POST /temporary-blocks/{block_id}/cancel

  let response5 = http.post(
    `${BASE_URL}/temporary-blocks/cancel-test-id/cancel`,
    JSON.stringify({
      reason: "Load test cancellation",
    }),
    params
  );

  // Customize these checks based on your API's expected behavior
  check(response5, {
    "POST /temporary-blocks/{block_id}/cancel status is 200": (r) =>
      r.status === 200,
    // Adjust expected status code if needed (201 for created, 204 for no content, etc.)
    "POST /temporary-blocks/{block_id}/cancel response time < 500ms": (r) =>
      r.timings.duration < 500,
  }) || errorRate.add(1);

  sleep(1);
}
