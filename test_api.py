import asyncio
import httpx
from app.main import app

async def run_tests():
    print("========================================")
    print("TRIPWISE BACKEND REST API SUITE TEST")
    print("========================================")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Clean up any previous test user for idempotency
        from app.database import get_db
        with get_db() as conn:
            conn.execute("DELETE FROM users WHERE email = 'aarav.sharma@example.com'")
            conn.commit()

        # 1. Health & Root
        r = await client.get("/")
        assert r.status_code == 200, f"Root failed: {r.text}"
        print("[PASS] Root & API Meta: 200 OK")

        r = await client.get("/health")
        assert r.status_code == 200, f"Health check failed: {r.text}"
        print("[PASS] Health Check: 200 OK")

        # 2. Auth: Register (Youth, Senior, Adult)
        user_payload = {
            "name": "Aarav Sharma",
            "email": "aarav.sharma@example.com",
            "password": "SecurePassword123!",
            "age": 21,
            "phone": "+91 9876543210",
            "location": "Chennai"
        }
        r = await client.post("/api/auth/register", json=user_payload)
        assert r.status_code == 201, f"Register failed: {r.text}"
        reg_data = r.json()
        assert reg_data["user"]["age_bracket"] == "Youth/Student"
        token = reg_data["access_token"]
        print(f"[PASS] Register (Age 21 -> Youth/Student): 201 Created | Token received")

        # Duplicate Register Check
        r = await client.post("/api/auth/register", json=user_payload)
        assert r.status_code == 400, f"Duplicate check failed: {r.text}"
        print("[PASS] Duplicate Registration Rejection: 400 Bad Request")

        # 3. Auth: Login
        login_payload = {
            "email": "aarav.sharma@example.com",
            "password": "SecurePassword123!"
        }
        r = await client.post("/api/auth/login", json=login_payload)
        assert r.status_code == 200, f"Login failed: {r.text}"
        token = r.json()["access_token"]
        print("[PASS] Login: 200 OK")

        # 4. Auth: Profile (Protected)
        headers = {"Authorization": f"Bearer {token}"}
        r = await client.get("/api/auth/profile", headers=headers)
        assert r.status_code == 200, f"Profile failed: {r.text}"
        print(f"[PASS] Protected Profile: 200 OK (User: {r.json()['name']})")

        # Invalid Token Check
        r = await client.get("/api/auth/profile", headers={"Authorization": "Bearer invalid_token"})
        assert r.status_code == 401, f"Unauthorized check failed: {r.text}"
        print("[PASS] Invalid Token Rejection: 401 Unauthorized")

        # 5. Destinations: List, Filter, Search, Sort
        r = await client.get("/api/destinations?city=Chennai&category=attractions")
        assert r.status_code == 200, f"Destinations list failed: {r.text}"
        dest_list = r.json()
        assert dest_list["total"] > 0
        print(f"[PASS] Destinations Discovery (Chennai attractions): 200 OK | {dest_list['total']} found")

        # Destination details + Live Weather + AQI
        dest_id = dest_list["destinations"][0]["id"]
        r = await client.get(f"/api/destinations/{dest_id}")
        assert r.status_code == 200, f"Destination details failed: {r.text}"
        d_detail = r.json()
        assert "live_environment" in d_detail
        print(f"[PASS] Destination Details & Telemetry ({d_detail['destination']['name']}): 200 OK | Temp: {d_detail['live_environment']['temperature_c']}C, AQI: {d_detail['live_environment']['aqi']}")

        # Non-existent ID Check
        r = await client.get("/api/destinations/non_existent_id_999")
        assert r.status_code == 404
        print("[PASS] Destination 404 Check: 404 Not Found")

        # 6. Environment Telemetry Feed
        r = await client.get("/api/environment-status?city=Chennai")
        assert r.status_code == 200, f"Environment feed failed: {r.text}"
        env_resp = r.json()
        assert len(env_resp["news_headlines"]) > 0
        print(f"[PASS] Environment Feed (Weather, AQI & News): 200 OK | Advisory: {env_resp['safety_advisory'][:60]}...")

        # 7. AI Smart Trip Planner
        ai_payload = {
            "destination": "Goa",
            "duration_days": 3,
            "start_date": "2026-11-10",
            "travel_priority": "couple_romantic",
            "max_budget": 12000.0,
            "user_age": 26
        }
        r = await client.post("/api/ai/plan-trip", json=ai_payload, headers=headers)
        assert r.status_code == 200, f"AI plan failed: {r.text}"
        ai_plan = r.json()
        assert ai_plan["cost_breakdown"]["within_budget"] is True
        assert len(ai_plan["daily_itinerary"]) == 3
        print(f"[PASS] AI Smart Trip Planner: 200 OK | Viability Score: {ai_plan['travel_viability_score']}% | Total Cost: Rs {ai_plan['cost_breakdown']['total_estimated_cost']} <= Rs {ai_plan['max_budget']}")

        # AI Budget under minimum threshold check
        bad_ai_payload = {
            "destination": "Goa",
            "duration_days": 5,
            "start_date": "2026-11-10",
            "travel_priority": "solo_adventure",
            "max_budget": 500.0,  # 5 days requires at least Rs 2500
            "user_age": 22
        }
        r = await client.post("/api/ai/plan-trip", json=bad_ai_payload, headers=headers)
        assert r.status_code == 400
        print("[PASS] AI Budget Threshold Enforcement: 400 Bad Request")

        # 8. Itinerary Persistence (CRUD)
        itin_payload = {
            "destination_id": dest_id,
            "destination_name": "Marina Beach Promenade & Lighthouse",
            "category": "attractions",
            "day_number": 1,
            "notes": "Watch sunset from lighthouse elevator and try hot filter coffee",
            "cost_estimate": 150.0
        }
        r = await client.post("/api/itinerary", json=itin_payload, headers=headers)
        assert r.status_code == 201, f"Itinerary add failed: {r.text}"
        created_item = r.json()
        item_id = created_item["id"]
        print(f"[PASS] Add Itinerary Item: 201 Created (ID: {item_id})")

        r = await client.get("/api/itinerary", headers=headers)
        assert r.status_code == 200, f"Get itinerary failed: {r.text}"
        itin_list = r.json()
        assert itin_list["total_items"] >= 1
        print(f"[PASS] Get Itinerary: 200 OK ({itin_list['total_items']} items saved, total: Rs {itin_list['total_estimated_budget']})")

        r = await client.delete(f"/api/itinerary/{item_id}", headers=headers)
        assert r.status_code == 200, f"Delete itinerary failed: {r.text}"
        print(f"[PASS] Delete Itinerary Item: 200 OK")

        r = await client.delete(f"/api/itinerary/{item_id}", headers=headers)
        assert r.status_code == 404
        print(f"[PASS] Delete Non-existent Item: 404 Not Found")

        # 9. Travel Packages & Payments
        r = await client.get("/api/packages?destination=Chennai")
        assert r.status_code == 200, f"Packages list failed: {r.text}"
        pkgs = r.json()
        assert pkgs["total"] > 0
        pkg = pkgs["packages"][0]
        print(f"[PASS] Packages Discovery: 200 OK | Found {pkgs['total']} options ({pkg['title']})")

        # Create Checkout Order
        checkout_payload = {
            "item_id": pkg["id"],
            "item_type": "package",
            "item_name": pkg["title"],
            "amount": pkg["price"],
            "currency": "INR"
        }
        r = await client.post("/api/payments/create-checkout", json=checkout_payload, headers=headers)
        assert r.status_code == 201, f"Create checkout failed: {r.text}"
        order_info = r.json()
        booking_ref = order_info["booking_reference"]
        order_id = order_info["order_id"]
        print(f"[PASS] Sandbox Payment Checkout: 201 Created | Order: {order_id} | Ref: {booking_ref}")

        # Verify Payment & Generate Digital Receipt
        verify_payload = {
            "booking_reference": booking_ref,
            "order_id": order_id,
            "payment_id": f"pay_mock_{order_id[-8:]}",
            "signature": "mock_valid_signature"
        }
        r = await client.post("/api/payments/verify", json=verify_payload)
        assert r.status_code == 200, f"Verify failed: {r.text}"
        verify_res = r.json()
        assert verify_res["status"] == "confirmed"
        print(f"[PASS] Payment Signature Verification & Receipt: 200 OK | Receipt: {verify_res['receipt_url']}")

        # Fetch Receipt
        r = await client.get(f"/api/payments/receipt/{booking_ref}")
        assert r.status_code == 200
        assert r.json()["status"] == "confirmed"
        print(f"[PASS] Digital Booking Receipt Retrieval: 200 OK")

    print("========================================")
    print("ALL API ENDPOINTS TESTED AND VERIFIED!")
    print("========================================")

if __name__ == "__main__":
    asyncio.run(run_tests())
