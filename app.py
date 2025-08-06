import streamlit as st
import requests
import xmltodict
import pandas as pd

# --- API 설정 ---
API_KEY = "bae2a59fb9ad4d27be4c243ae11bdb90"
CCTV_POS_URL = "http://www.utic.go.kr/guide/openCctvPos.do"
CCTV_STRM_URL = "http://www.utic.go.kr/guide/openCctvStrm.do"

# --- 함수 정의 ---
def get_cctv_list(location):
    """특정 위치의 CCTV 목록을 가져옵니다."""
    params = {"key": API_KEY, "search_text": location}
    try:
        response = requests.get(CCTV_POS_URL, params=params)
        response.raise_for_status()
        data = xmltodict.parse(response.content)
        cctv_list = data.get("cctv", {}).get("data", [])
        # API가 단일 항목을 반환할 때 리스트가 아닌 dict로 오는 경우 처리
        if cctv_list and not isinstance(cctv_list, list):
            cctv_list = [cctv_list]
        return cctv_list
    except requests.exceptions.RequestException as e:
        st.error(f"API 요청 중 오류 발생: {e}")
        return None
    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {e}")
        return None

def get_stream_url(cctv_id):
    """특정 CCTV의 실시간 영상 URL을 가져옵니다."""
    params = {"key": API_KEY, "cctvId": cctv_id}
    try:
        response = requests.get(CCTV_STRM_URL, params=params)
        response.raise_for_status()
        data = xmltodict.parse(response.content)
        return data.get("cctv", {}).get("cctvurl")
    except requests.exceptions.RequestException as e:
        st.error(f"영상 주소 요청 중 오류 발생: {e}")
        return None
    except Exception as e:
        st.error(f"영상 주소 처리 중 오류 발생: {e}")
        return None

# --- Streamlit UI --- 
st.set_page_config(layout="wide")
st.title("CCTV 실시간 영상 뷰어")

# 세션 상태 초기화
if 'cctv_data' not in st.session_state:
    st.session_state.cctv_data = []

# 검색 폼
with st.form(key='search_form'):
    location_input = st.text_input("검색할 위치를 입력하세요 (예: 서울, 강남대로)")
    submit_button = st.form_submit_button(label='검색')

if submit_button and location_input:
    with st.spinner('CCTV 정보를 검색 중입니다...'):
        st.session_state.cctv_data = get_cctv_list(location_input)

# 검색 결과 표시
if st.session_state.cctv_data:
    st.subheader("CCTV 검색 결과")
    df = pd.DataFrame(st.session_state.cctv_data)
    # 보여줄 컬럼만 선택 및 이름 변경
    display_df = df[["cctvname", "coordx", "coordy"]].rename(
        columns={"cctvname": "CCTV 이름", "coordx": "경도", "coordy": "위도"}
    )
    st.dataframe(display_df)

    # 영상 선택
    st.subheader("실시간 영상 보기")
    cctv_names = [cctv.get('cctvname', '이름 없음') for cctv in st.session_state.cctv_data]
    selected_cctv_name = st.selectbox("영상을 볼 CCTV를 선택하세요:", options=cctv_names)

    if selected_cctv_name:
        # 선택된 이름으로 전체 CCTV 데이터 찾기
        selected_cctv = next((cctv for cctv in st.session_state.cctv_data if cctv.get('cctvname') == selected_cctv_name), None)
        if selected_cctv:
            cctv_id = selected_cctv.get('cctvid')
            with st.spinner('영상 주소를 가져오는 중...'):
                stream_url = get_stream_url(cctv_id)
                if stream_url:
                    st.video(stream_url)
                else:
                    st.warning("해당 CCTV의 영상 주소를 가져올 수 없습니다.")
elif submit_button:
    st.info("검색된 CCTV가 없습니다. 다른 키워드로 검색해 보세요.")
