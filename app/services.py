import httpx
import asyncio

class ExternalAPIException(Exception):
    def __init__(self, message: str, status_code: int = 502):
        self.message = message
        self.status_code = status_code

async def fetch_api(client, url):
    try:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
    except Exception:
        raise ExternalAPIException("Upstream or server failure", 502)

async def get_combined_data(name: str):
    async with httpx.AsyncClient() as client:
        try:
            gender_data, age_data, nat_data = await asyncio.gather(
                fetch_api(client, f"https://api.genderize.io?name={name}"),
                fetch_api(client, f"https://api.agify.io?name={name}"),
                fetch_api(client, f"https://api.nationalize.io?name={name}")
            )
        except ExternalAPIException as e:
            raise e
        except Exception:
            raise ExternalAPIException("Upstream or server failure", 502)

    if gender_data.get("gender") is None or gender_data.get("count") == 0:
        raise ExternalAPIException("Genderize returned an invalid response", 502)
    
    if age_data.get("age") is None:
        raise ExternalAPIException("Agify returned an invalid response", 502)
    
    if not nat_data.get("country"):
        raise ExternalAPIException("Nationalize returned an invalid response", 502)

    best_country = max(nat_data["country"], key=lambda c: c["probability"])

    age = age_data["age"]
    if age <= 12:
        age_group = "child"
    elif age <= 19:
        age_group = "teenager"
    elif age <= 59:
        age_group = "adult"
    else:
        age_group = "senior"

    return {
        "name": name,
        "gender": gender_data["gender"],
        "gender_probability": gender_data["probability"],
        "sample_size": gender_data["count"],
        "age": age,
        "age_group": age_group,
        "country_id": best_country["country_id"],
        "country_probability": best_country["probability"],
    }
