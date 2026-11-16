from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings
app=FastAPI(title='Compensation Equity Intelligence API',version='1.0.0',description='Auditable compensation comparison and review workflow')
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.include_router(router,prefix=settings.api_prefix)
@app.get('/')
def root(): return {'service':'Compensation Equity Intelligence','docs':'/docs'}
