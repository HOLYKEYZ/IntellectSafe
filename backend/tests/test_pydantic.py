import os
os.environ['TEST_KEY'] = 'value'
from pydantic_settings import BaseSettings
from pydantic import Field

class T(BaseSettings):
    x: str = Field(None, validation_alias='TEST_KEY')
    
print(T().x)
