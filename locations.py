import os
from typing import List, Tuple
from google.maps import places


class Location:
    def __init__(self, name: str, address: str, coords: Tuple[float, float]):
        self.name = name
        self.address = address
        self.coords = coords


class LocationResolver:
    def __init__(self):
        self.client = places.PlacesClient(
            client_options={"api_key": os.getenv("GOOGLE_PLACES_API_KEY")})

    def resolve(self, query: str, region: str) -> List[Location]:
        search_query = f"{query} in {region}"
        request = places.SearchTextRequest(text_query=search_query)
        fields = "places.displayName,places.formatted_address,places.location"
        metadata = [("x-goog-fieldmask", fields)]
        response = self.client.search_text(request, metadata=metadata)
        locations = []
        for place in response.places:
            location = Location(place.display_name.__str__(),
                                place.formatted_address,
                                (place.location.latitude,
                                 place.location.longitude))
            locations.append(location)
        return locations
