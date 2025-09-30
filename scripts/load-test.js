import http from 'k6/http';
import { check, sleep } from 'k6';

// Test configuration
export let options = {
  stages: [
    { duration: '30s', target: 10 }, // Ramp up to 10 users
    { duration: '1m', target: 10 },  // Stay at 10 users
    { duration: '30s', target: 0 },  // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests must complete below 500ms
    http_req_failed: ['rate<0.1'],    // Error rate must be below 10%
  },
};

const BASE_URL = 'http://localhost:8080/api';

// Test data
const testUser = {
  username: 'loadtest_user',
  email: 'loadtest@example.com',
  password: 'loadtest123'
};

let authToken = '';

export function setup() {
  // Register test user
  let registerResponse = http.post(`${BASE_URL}/auth/register`, JSON.stringify(testUser), {
    headers: { 'Content-Type': 'application/json' },
  });
  
  if (registerResponse.status === 201 || registerResponse.status === 409) {
    // Login to get token
    let loginResponse = http.post(`${BASE_URL}/auth/login`, JSON.stringify({
      username: testUser.username,
      password: testUser.password
    }), {
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (loginResponse.status === 200) {
      let loginData = JSON.parse(loginResponse.body);
      return { token: loginData.token };
    }
  }
  
  return { token: '' };
}

export default function(data) {
  // Test 1: Health Check
  let healthResponse = http.get(`${BASE_URL}/health`);
  check(healthResponse, {
    'health check status is 200': (r) => r.status === 200,
    'health check response time < 200ms': (r) => r.timings.duration < 200,
  });

  sleep(1);

  // Test 2: Authentication endpoints
  if (data.token) {
    // Verify token
    let verifyResponse = http.post(`${BASE_URL}/auth/verify`, JSON.stringify({
      token: data.token
    }), {
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${data.token}`
      },
    });
    
    check(verifyResponse, {
      'token verification status is 200': (r) => r.status === 200,
      'token verification response time < 300ms': (r) => r.timings.duration < 300,
    });

    sleep(1);

    // Get user profile
    let profileResponse = http.get(`${BASE_URL}/auth/profile`, {
      headers: { 
        'Authorization': `Bearer ${data.token}`
      },
    });
    
    check(profileResponse, {
      'profile fetch status is 200': (r) => r.status === 200,
      'profile fetch response time < 300ms': (r) => r.timings.duration < 300,
    });

    sleep(1);

    // Test 3: Video processing endpoints
    // Get video stats
    let statsResponse = http.get(`${BASE_URL}/video/stats`, {
      headers: { 
        'Authorization': `Bearer ${data.token}`
      },
    });
    
    check(statsResponse, {
      'video stats status is 200': (r) => r.status === 200,
      'video stats response time < 500ms': (r) => r.timings.duration < 500,
    });

    sleep(1);

    // Get video jobs
    let jobsResponse = http.get(`${BASE_URL}/video/jobs`, {
      headers: { 
        'Authorization': `Bearer ${data.token}`
      },
    });
    
    check(jobsResponse, {
      'video jobs status is 200': (r) => r.status === 200,
      'video jobs response time < 500ms': (r) => r.timings.duration < 500,
    });
  }

  sleep(1);

  // Test 4: Health aggregation
  let healthAllResponse = http.get(`${BASE_URL}/health/all`);
  check(healthAllResponse, {
    'health aggregation status is 200 or 503': (r) => r.status === 200 || r.status === 503,
    'health aggregation response time < 1000ms': (r) => r.timings.duration < 1000,
  });

  sleep(2);
}

export function teardown(data) {
  // Cleanup if needed
  console.log('Load test completed');
}

