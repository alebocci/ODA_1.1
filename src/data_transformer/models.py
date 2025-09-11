
from sqlalchemy import Column, Integer, String, Text, JSON, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# modelli per la creazione delle tabelle nel database
class MappingFunction(Base):
    __tablename__ = 'mapping_functions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mapping_name = Column(String(255), unique=True, nullable=False)
    mapping_function = Column(Text, nullable=False)
    schema_dest = Column(JSON)
    schema_input = Column(JSON)
    schema_dest_name = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())

class MappingDGLink(Base):
    __tablename__ = 'mapping_dg_links'
    mapping_id = Column(Integer, ForeignKey('mapping_functions.id'), primary_key=True)
    generator_id = Column(String(255), primary_key=True)
    topic = Column(String(255), primary_key=True)
    created_at = Column(TIMESTAMP, server_default=func.now())