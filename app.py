import streamlit as st

# 1. 음식 데이터 (딕셔너리 구조)
FOOD_DATA = {
    "현미밥": {"칼로리": 300, "탄수화물": 65, "단백질": 6, "지방": 1},
    "닭가슴살 구이": {"칼로리": 165, "탄수화물": 0, "단백질": 31, "지방": 3},
    "연어 구이": {"칼로리": 200, "탄수화물": 0, "단백질": 22, "지방": 13},
    "계란 프라이": {"칼로리": 70, "탄수화물": 0.5, "단백질": 6, "지방": 5},
    "사과": {"칼로리": 90, "탄수화물": 24, "단백질": 0.5, "지방": 0.3},
    "샐러드 (드레싱 포함)": {"칼로리": 120, "탄수화물": 10, "단백질": 2, "지방": 8},
    "라면": {"칼로리": 500, "탄수화물": 80, "단백질": 10, "지방": 15},
    "피자 (1조각)": {"칼로리": 250, "탄수화물": 30, "단백질": 12, "지방": 10},
}

# 기본 페이지 설정
st.set_page_config(page_title="식사 균형 계산기", layout="centered")
st.title("🥗 오늘 나의 식사 균형 계산기")
st.write("오늘 먹은 음식을 고르면 영양 균형을 분석해 드립니다.")

st.divider()

# 2. 사용자 음식 선택 (기본값 설정 오류 방지를 위해 리스트 체크)
selected_foods = st.multiselect(
    "오늘 어떤 음식을 드셨나요? (여러 개 선택 가능)",
    options=list(FOOD_DATA.keys()),
    default=["현미밥", "닭가슴살 구이"]
)

# 변수 초기화
total_cal = 0
total_carbs = 0
total_protein = 0
total_fat = 0

# 3. 영양소 총합 계산
for food in selected_foods:
    if food in FOOD_DATA:  # 키 에러 방지
        total_cal += FOOD_DATA[food]["칼로리"]
        total_carbs += FOOD_DATA[food]["탄수화물"]
        total_protein += FOOD_DATA[food]["단백질"]
        total_fat += FOOD_DATA[food]["지방"]

# 4. 결과 출력 구문
if selected_foods:
    st.subheader("📊 총 영양성분 요약")
    
    # 가독성 좋은 대시보드 레이아웃
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 칼로리", f"{total_cal} kcal")
    col2.metric("탄수화물", f"{total_carbs}g")
    col3.metric("단백질", f"{total_protein}g")
    col4.metric("지방", f"{total_fat}g")
    
    st.divider()
    
    # 에너지를 내는 칼로리 비율 계산 (탄4, 단4, 지9)
    carbs_kcal = total_carbs * 4
    protein_kcal = total_protein * 4
    fat_kcal = total_fat * 9
    total_kcal_calc = carbs_kcal + protein_kcal + fat_kcal
    
    # 0으로 나누는 에러(ZeroDivisionError) 방지
    if total_kcal_calc > 0:
        st.subheader("🍕 탄/단/지 비율 분석")
        
        # 스트림릿 내장 바 차트용 데이터 구성
        chart_data = {
            "탄수화물 (kcal)": [carbs_kcal],
            "단백질 (kcal)": [protein_kcal],
            "지방 (kcal)": [fat_kcal]
        }
        
        # 가로형 막대 그래프로 비율 시각화
        st.bar_chart(chart_data)
        
        # 비율 계산
        carbs_ratio = carbs_kcal / total_kcal_calc
        protein_ratio = protein_kcal / total_kcal_calc
        fat_ratio = fat_kcal / total_kcal_calc
        
        # 5. 영양 균형 피드백
        st.subheader("💡 맞춤형 식단 피드백")
        if protein_ratio < 0.2:
            st.warning("⚠️ 근성장과 대사를 위해 단백질 비율이 낮습니다! 닭가슴살, 계란, 두부 등을 더 챙겨 드세요.")
        elif carbs_ratio > 0.65:
            st.warning("⚠️ 탄수화물 비중이 높은 편입니다. 정제 탄수화물(면, 빵) 대신 단백질 반찬을 늘려보세요.")
        elif fat_ratio > 0.4:
            st.warning("⚠️ 지방으로 섭취하는 칼로리가 많습니다. 튀긴 음식이나 소스류를 조금 줄여보시는 걸 권장합니다.")
        else:
            st.success("🎉 탄수화물, 단백질, 지방의 균형이 아주 이상적입니다! 이대로만 드세요.")
    else:
        st.info("선택한 음식들의 영양성분(칼로리)이 0입니다. 다른 음식을 조합해 보세요.")
else:
    st.info("💡 위 메뉴에서 음식을 선택하시면 실시간 분석이 시작됩니다.")
    
