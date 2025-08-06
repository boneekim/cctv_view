import streamlit as st
import requests
import xmltodict
import pandas as pd

# --- API 설정 ---
# 공공데이터포털에서 발급받은 일반 인증키 (URL 인코딩되지 않은 원본 키)
API_KEY = "bae2a59fb9ad4d27be4c243ae11bdb90"
# 공공데이터포털 API URL
API_URL = "http://apis.data.go.kr/1741000/CctvInfoService/getCctvInfo"

# --- 함수 정의 ---
def get_cctv_data(location):
    """공공데이터포털 API를 사용하여 특정 위치의 CCTV 정보를 가져옵니다."""
    params = {
        'serviceKey': API_KEY,
        'type': 'xml',          # 응답 형식
        'cctvType': '1',        # 1:실시간스트리밍, 2:동영상, 3:정지영상
        'minX': '126.0',
        'maxX': '128.0',
        'minY': '36.0',
        'maxY': '38.0',
        'pageNo': '1',
        'numOfRows': '100',     # 한 번에 가져올 데이터 수
    }
    try:
        # 위치 정보는 API 자체 필터링 기능이 없어, 가져온 후 이름으로 필터링합니다.
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = xmltodict.parse(response.content)
        
        # 데이터 경로 확인 및 추출
        response_data = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
        if not response_data:
            return []

        # API가 단일 항목을 반환할 때 리스트가 아닌 dict로 오는 경우 처리
        if not isinstance(response_data, list):
            response_data = [response_data]

        # 'location'을 포함하는 CCTV만 필터링
        filtered_data = [item for item in response_data if location in item.get('cctvname', '')]
        return filtered_data

    except requests.exceptions.RequestException as e:
        st.error(f"API 요청 중 오류 발생: {e}")
        return None
    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {e}")
        return None

# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("CCTV 실시간 영상 뷰어 (공공데이터포털)")

# 세션 상태 초기화
if 'cctv_data' not in st.session_state:
    st.session_state.cctv_data = []

# 검색 폼
with st.form(key='search_form'):
    location_input = st.text_input("검색할 위치를 입력하세요 (예: 서울, 강남대로)")
    submit_button = st.form_submit_button(label='검색')

if submit_button and location_input:
    with st.spinner('CCTV 정보를 검색 중입니다...'):
        st.session_state.cctv_data = get_cctv_data(location_input)

# 검색 결과 표시
if st.session_state.cctv_data:
    st.subheader("CCTV 검색 결과")
    df = pd.DataFrame(st.session_state.cctv_data)
    
    # 보여줄 컬럼만 선택 및 이름 변경
    display_df = df[["cctvname", "cctvurl"]].rename(
        columns={"cctvname": "CCTV 이름", "cctvurl": "영상 URL"}
    )
    st.dataframe(display_df)

    # 영상 선택
    st.subheader("실시간 영상 보기")
    cctv_options = {item.get('cctvname'): item.get('cctvurl') for item in st.session_state.cctv_data}
    selected_cctv_name = st.selectbox("영상을 볼 CCTV를 선택하세요:", options=cctv_options.keys())

    if selected_cctv_name:
        stream_url = cctv_options[selected_cctv_name]
        if stream_url and stream_url.startswith('http'):
            st.video(stream_url)
        else:
            st.warning("유효한 영상 주소가 아닙니다.")

elif submit_button:
    st.info("검색된 CCTV가 없습니다. 다른 키워드로 검색해 보세요.")