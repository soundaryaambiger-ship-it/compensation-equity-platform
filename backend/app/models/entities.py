from sqlalchemy import String, Integer, Float, Date, DateTime, Boolean, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base
class Role(Base):
    __tablename__='roles'; id:Mapped[str]=mapped_column(String,primary_key=True); name:Mapped[str]=mapped_column(String,unique=True); family:Mapped[str]=mapped_column(String)
class Level(Base):
    __tablename__='levels'; id:Mapped[str]=mapped_column(String,primary_key=True); name:Mapped[str]=mapped_column(String,unique=True); rank:Mapped[int]=mapped_column(Integer,unique=True)
class Location(Base):
    __tablename__='locations'; id:Mapped[str]=mapped_column(String,primary_key=True); name:Mapped[str]=mapped_column(String,unique=True); country:Mapped[str]=mapped_column(String); currency:Mapped[str]=mapped_column(String); fx_to_inr:Mapped[float]=mapped_column(Float)
class Employee(Base):
    __tablename__='employees'; id:Mapped[str]=mapped_column(String,primary_key=True); name:Mapped[str]=mapped_column(String); role_id:Mapped[str]=mapped_column(ForeignKey('roles.id')); level_id:Mapped[str]=mapped_column(ForeignKey('levels.id')); location_id:Mapped[str]=mapped_column(ForeignKey('locations.id')); hire_date:Mapped[datetime]=mapped_column(Date); employment_status:Mapped[str]=mapped_column(String,default='ACTIVE'); fte:Mapped[float]=mapped_column(Float,default=1.0)
class CompensationBand(Base):
    __tablename__='compensation_bands'; id:Mapped[str]=mapped_column(String,primary_key=True); role_id:Mapped[str]=mapped_column(ForeignKey('roles.id')); level_id:Mapped[str]=mapped_column(ForeignKey('levels.id')); location_id:Mapped[str]=mapped_column(ForeignKey('locations.id')); currency:Mapped[str]=mapped_column(String); minimum:Mapped[float]=mapped_column(Float); midpoint:Mapped[float]=mapped_column(Float); maximum:Mapped[float]=mapped_column(Float); effective_from:Mapped[datetime]=mapped_column(Date); effective_to:Mapped[datetime|None]=mapped_column(Date,nullable=True)
class SalaryRecord(Base):
    __tablename__='salary_records'; id:Mapped[str]=mapped_column(String,primary_key=True); employee_id:Mapped[str]=mapped_column(ForeignKey('employees.id')); effective_date:Mapped[datetime]=mapped_column(Date); base_salary:Mapped[float]=mapped_column(Float); currency:Mapped[str]=mapped_column(String); fte:Mapped[float]=mapped_column(Float); annualized_inr:Mapped[float|None]=mapped_column(Float,nullable=True); band_id:Mapped[str|None]=mapped_column(ForeignKey('compensation_bands.id'),nullable=True); change_reason:Mapped[str]=mapped_column(String); issue_type:Mapped[str]=mapped_column(String,default='')
class PerformanceEvidence(Base):
    __tablename__='performance_evidence'; id:Mapped[str]=mapped_column(String,primary_key=True); employee_id:Mapped[str]=mapped_column(ForeignKey('employees.id')); period_start:Mapped[datetime]=mapped_column(Date); period_end:Mapped[datetime]=mapped_column(Date); rating:Mapped[float]=mapped_column(Float); evidence_note:Mapped[str]=mapped_column(Text)
class Tenure(Base):
    __tablename__='tenure'; id:Mapped[str]=mapped_column(String,primary_key=True); employee_id:Mapped[str]=mapped_column(ForeignKey('employees.id')); as_of_date:Mapped[datetime]=mapped_column(Date); years:Mapped[float]=mapped_column(Float)
class Promotion(Base):
    __tablename__='promotions'; id:Mapped[str]=mapped_column(String,primary_key=True); employee_id:Mapped[str]=mapped_column(ForeignKey('employees.id')); from_level_id:Mapped[str]=mapped_column(ForeignKey('levels.id')); to_level_id:Mapped[str]=mapped_column(ForeignKey('levels.id')); effective_date:Mapped[datetime]=mapped_column(Date); approved_by:Mapped[str]=mapped_column(String)
class AdjustmentProposal(Base):
    __tablename__='adjustment_proposals'; id:Mapped[str]=mapped_column(String,primary_key=True); employee_id:Mapped[str]=mapped_column(ForeignKey('employees.id')); proposed_amount_inr:Mapped[float]=mapped_column(Float); reason:Mapped[str]=mapped_column(Text); evidence_json:Mapped[str]=mapped_column(Text); status:Mapped[str]=mapped_column(String,default='PENDING'); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow); manager_approved_by:Mapped[str|None]=mapped_column(String,nullable=True); hr_approved_by:Mapped[str|None]=mapped_column(String,nullable=True)
class AuditEvent(Base):
    __tablename__='audit_events'; id:Mapped[str]=mapped_column(String,primary_key=True); entity_type:Mapped[str]=mapped_column(String); entity_id:Mapped[str]=mapped_column(String); event_type:Mapped[str]=mapped_column(String); actor:Mapped[str]=mapped_column(String); details:Mapped[str]=mapped_column(Text); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class ComparableGroup(Base):
    __tablename__='comparable_groups'; id:Mapped[str]=mapped_column(String,primary_key=True); name:Mapped[str]=mapped_column(String); rationale:Mapped[str]=mapped_column(Text); effective_from:Mapped[datetime]=mapped_column(Date); effective_to:Mapped[datetime|None]=mapped_column(Date,nullable=True)
class ComparableGroupMember(Base):
    __tablename__='comparable_group_members'; group_id:Mapped[str]=mapped_column(ForeignKey('comparable_groups.id'),primary_key=True); employee_id:Mapped[str]=mapped_column(ForeignKey('employees.id'),primary_key=True); added_at:Mapped[datetime]=mapped_column(Date); rationale:Mapped[str]=mapped_column(Text)
