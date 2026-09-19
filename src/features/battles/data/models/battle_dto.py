from pydantic import BaseModel, ConfigDict, model_validator
import json

class Battle(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    started_timestamp:int
    user_id: int
    status: str = "none"
    data: dict = {}
    log: dict = {}

    @model_validator(mode='before')
    @classmethod
    def parse_json_fields(cls, value):
        if not isinstance(value, dict):
            for field_name in ['data', 'log']:
                raw_val = getattr(value, field_name, None)
                if isinstance(raw_val, str):
                    try:
                        setattr(value, field_name, json.loads(raw_val))
                    except json.JSONDecodeError:
                        setattr(value, field_name, {})
            return value

        for field_name in ['data', 'log']:
            if isinstance(value.get(field_name), str):
                try:
                    value[field_name] = json.loads(value[field_name])
                except json.JSONDecodeError:
                    value[field_name] = {}
                    
        return value
    
    @model_validator(mode='before')
    @classmethod
    def parse_json_attributes(cls, log_dict):
        if not isinstance(log_dict, dict):
            raw_data = getattr(log_dict, 'log', None)
            if isinstance(raw_data, str):
                try:
                    log_dict.log = json.loads(raw_data)
                except json.JSONDecodeError:
                    log_dict.log = {}
        
        elif isinstance(log_dict.get('log'), str):
            try:
                log_dict['log'] = json.loads(log_dict['log'])
            except json.JSONDecodeError:
                log_dict['log'] = {}
                
        return log_dict