# check_env.py
import os, sys, requests
from dotenv import load_dotenv

def mask(s: str, show: int = 6) -> str:
    if not s:
        return "(VACÍO)"
    return f"{s[:show]}*** ({len(s)} chars)"

def main():
    # 1) Cargar .env local (del directorio actual)
    env_loaded = load_dotenv(dotenv_path=".env", override=True)
    print(f"[1/3] .env cargado: {env_loaded}")

    # 2) Leer variables esperadas
    AMADEUS_BASE_URL = os.getenv("AMADEUS_BASE_URL", "").strip()
    AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY", "").strip()
    AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET", "").strip()

    print("[2/3] Variables leídas:")
    print(f"  AMADEUS_BASE_URL = {AMADEUS_BASE_URL or '(VACÍO)'}")
    print(f"  AMADEUS_API_KEY  = {mask(AMADEUS_API_KEY)}")
    print(f"  AMADEUS_API_SECRET = {mask(AMADEUS_API_SECRET)}")

    missing = []
    if not AMADEUS_BASE_URL: missing.append("AMADEUS_BASE_URL")
    if not AMADEUS_API_KEY:  missing.append("AMADEUS_API_KEY")
    if not AMADEUS_API_SECRET: missing.append("AMADEUS_API_SECRET")

    if missing:
        print(f"\n[ERROR] Faltan variables en .env: {', '.join(missing)}")
        sys.exit(2)

    # 3) Probar token OAuth2 en Amadeus
    auth_url = f"{AMADEUS_BASE_URL}/v1/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = (
        f"grant_type=client_credentials"
        f"&client_id={AMADEUS_API_KEY}"
        f"&client_secret={AMADEUS_API_SECRET}"
    )
    print(f"\n[3/3] Solicitando token a: {auth_url}")

    try:
        resp = requests.post(auth_url, data=payload, headers=headers, timeout=12)
        print(f"  HTTP {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("access_token", "")
            print(f"  ✅ access_token = {mask(token, show=12)}")
            print("  ✅ ¡Credenciales válidas y .env OK!\n")
            sys.exit(0)
        else:
            print("  ❌ Respuesta no OK:")
            print(resp.text[:500])
            sys.exit(1)
    except Exception as e:
        print(f"  ❌ Excepción solicitando token: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
