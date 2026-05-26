import streamlit as st
import plotly.express as px
import pandas as pd

# 1. 간단한 음식 영양성분 데이터 (1인분 기준 가상 데이터)
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

# 앱 제목 설정
st.set_page_config(page_title="식사 균형 계산기", layout="centered")
st.title("🥗 오늘 나의 식사 균형 계산기")
st.write("오늘 먹은 음식을 선택하면 탄/단/지 영양 균형을 분석해 드립니다!")

st.divider()

# 2. 사용자 입력 받기 (멀티셀렉트)
selected_foods = st.multiselect(
    "오늘 어떤 음식을 드셨나요? (여러 개 선택 가능)",
    options=list(FOOD_DATA.keys()),
    default=["현미밥", "닭가슴살 구이"]
)

# 3. 영양소 총합 계산
total_cal = 0
total_carbs = 0
total_protein = 0
total_fat = 0

for food in selected_foods:
    total_cal += FOOD_DATA[food]["칼로리"]
    total_carbs += FOOD_DATA[food]["탄수화물"]
    total_protein += FOOD_DATA[food]["단백질"]
    total_fat += FOOD_DATA[food]["지방"]

# 음식을 선택했을 때만 결과 표시
if selected_foods:
    # 대시보드 레이아웃 (총 칼로리 및 영양소 표시)
    st.subheader("📊 총 영양성분 요약")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 칼로리", f"{total_cal} kcal")
    col2.metric("탄수화물", f"{total_carbs}g")
    col3.metric("단백질", f"{total_protein}g")
    col4.metric("지방", f"{total_fat}g")
    
    st.divider()
    
    # 4. 탄단지 비율 시각화 (파이 차트)
    st.subheader("🍕 탄/단/지 비율 분석")
    
    # 칼로리 비율 계산을 위한 데이터프레임 생성 (1g당 탄수화물 4kcal, 단백질 4kcal, 지방 9kcal)
    carbs_kcal = total_carbs * 4
    protein_kcal = total_protein * 4
    fat_kcal = total_fat * 9
    total_kcal_calc = carbs_kcal + protein_kcal + fat_kcal
    
    if total_kcal_calc > 0:
        nutrients_df = pd.DataFrame({
            "영양소": ["탄수화물", "단백질", "지방"],
            "칼로리(kcal)": [carbs_kcal, protein_kcal, fat_kcal]
        })
        
        fig = px.pie(nutrients_df, values="칼로리(kcal)", names="영양소", 
                     color="영양소", color_discrete_map={"탄수화물":"#FFA07A", "단백질":"#20B2AA", "지방":"#FFD700"},
                     hole=0.4)
        st.plotly_chart(fig)
        
        # 5. 간단한 피드백 제공
        carbs_ratio = carbs_kcal / total_kcal_calc
        protein_ratio = protein_kcal / total_kcal_calc
        fat_ratio = fat_kcal / total_kcal_calc
        
        st.subheader("💡 맞춤형 식단 피드백")
        if protein_ratio < 0.2:
            st.warning("⚠️ 근성장을 위해 단백질 섭취량이 조금 부족해요! 닭가슴살이나 계란을 더 추가해 보세요.")
        elif carbs_ratio > 0.65:
            st.warning("⚠️ 탄수화물 비율이 다소 높습니다. 정제 탄수화물을 줄여보시는 건 어떨까요?")
        elif fat_ratio > 0.4:
            st.warning("⚠️ 지방 섭취 비중이 높습니다. 튀긴 음식보다는 구운 음식을 추천합니다.")
        else:
            st.success("🎉 탄수화물, 단백질, 지방의 균형이 아주 좋습니다! 이대로 유지해 보세요.")
            
    else:
        st.info("선택한 음식의 영양 성분이 0입니다.")
        
else:
    st.info("음식을 선택하시면 영양 균형 분석이 시작됩니다.")
