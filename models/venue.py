from pydantic import BaseModel

class Venue(BaseModel):
    name: str
    location: str
    price: str
    capacity: str
    rating: float
    reviews: int
    description: str