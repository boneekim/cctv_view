from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
import xmltodict
import json

app = FastAPI()

# 정적 파일 제공을 위한 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

API_KEY = "bae2a59fb9ad4d27be4c243ae11bdb90"
CCTV_POS_URL = "http://www.utic.go.kr/guide/openCctvPos.do"
CCTV_STRM_URL = "http://www.utic.go.kr/guide/openCctvStrm.do"

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.get("/cctv/{location}")
def get_cctv_by_location(location: str):
    params = {
        "key": API_KEY,
        "search_text": location
    }
    try:
        response = requests.get(CCTV_POS_URL, params=params)
        response.raise_for_status()
        data = xmltodict.parse(response.content)
        cctv_list = data.get("cctv", {}).get("data", [])
        if not cctv_list:
            return {"message": "해당 위치에 대한 CCTV 정보를 찾을 수 없습니다."}
        return {"cctv_list": cctv_list}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"API 요청 중 오류 발생: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 처리 중 오류 발생: {e}")

@app.get("/cctv/stream/{cctv_id}")
def get_cctv_stream(cctv_id: str):
    params = {
        "key": API_KEY,
        "cctvId": cctv_id
    }
    try:
        response = requests.get(CCTV_STRM_URL, params=params)
        response.raise_for_status()
        data = xmltodict.parse(response.content)
        stream_url = data.get("cctv", {}).get("cctvurl")
        if not stream_url:
            return {"message": "실시간 영상 정보를 가져올 수 없습니다."}
        return {"stream_url": stream_url}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"API 요청 중 오류 발생: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 처리 중 오류 발생: {e}")