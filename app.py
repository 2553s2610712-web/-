import streamlit as st
import numpy as np
import random

# 1. 페이지 설정 및 스타일 초기화
st.set_page_config(page_title="스트림릿 테트리스", layout="centered")

# CSS를 이용해 버튼 클릭 시 화면이 깜빡이거나 스크롤이 튀는 현상 방지
st.markdown("""
    <style>
    div.stButton > button { width: 100%; height: 50px; font-size: 18px; margin-bottom: 5px; }
    .block-container { padding-top: 2rem; max-width: 500px; }
    </style>
""", unsafe_allow_html=True)

GRID_ROWS = 20
GRID_COLS = 10

# 테트로미노 블록 데이터 (정수형 리스트로 명확히 정의)
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]]   # L
]

# 2. 게임 초기화 함수
def init_game():
    st.session_state.board = [[0] * GRID_COLS for _ in range(GRID_ROWS)]
    st.session_state.score = 0
    st.session_state.game_over = False
    spawn_block()

# 3. 새 블록 생성 함수
def spawn_block():
    st.session_state.current_shape = random.choice(SHAPES)
    st.session_state.block_row = 0
    # 가운데 정렬
    st.session_state.block_col = (GRID_COLS - len(st.session_state.current_shape[0])) // 2
    
    # 생성되자마자 충돌하면 게임 오버
    if check_collision(st.session_state.block_row, st.session_state.block_col, st.session_state.current_shape):
        st.session_state.game_over = True

# 4. 충돌 검사 함수 (벽, 바닥, 기존 블록 체크)
def check_collision(r, c, shape):
    for i in range(len(shape)):
        for j in range(len(shape[i])):
            if shape[i][j]:
                next_r = r + i
                next_c = c + j
                # 벽이나 바닥에 부딪힌 경우
                if next_r >= GRID_ROWS or next_c < 0 or next_c >= GRID_COLS:
                    return True
                # 기존에 쌓인 블록과 부딪힌 경우
                if next_r >= 0 and st.session_state.board[next_r][next_c]:
                    return True
    return False

# 5. 블록 고정 및 줄 지우기 함수
def freeze_block():
    r = st.session_state.block_row
    c = st.session_state.block_col
    shape = st.session_state.current_shape
    
    for i in range(len(shape)):
        for j in range(len(shape[i])):
            if shape[i][j] and (r + i) >= 0:
                st.session_state.board[r + i][c + j] = 1
                
    # 꽉 찬 줄 제거 로직 (오류 없는 필터링 방식)
    new_board = [row for row in st.session_state.board if any(cell == 0 for cell in row)]
    cleared_lines = GRID_ROWS - len(new_board)
    
    if cleared_lines > 0:
        # 지워진 만큼 위에 빈 줄 추가
        for _ in range(cleared_lines):
            new_board.insert(0, [0] * GRID_COLS)
        st.session_state.score += cleared_lines * 100
        st.session_state.board = new_board

    spawn_block()

# 6. 블록 조작 함수
def move(direction):
    if st.session_state.game_over:
        return
        
    r = st.session_state.block_row
    c = st.session_state.block_col
    shape = st.session_state.current_shape
    
    if direction == 'left':
        if not check_collision(r, c - 1, shape):
            st.session_state.block_col -= 1
    elif direction == 'right':
        if not check_collision(r, c + 1, shape):
            st.session_state.block_col += 1
    elif direction == 'down':
        if not check_collision(r + 1, c, shape):
            st.session_state.block_row += 1
        else:
            freeze_block()
    elif direction == 'rotate':
        # 행렬 회전 (에러 방지를 위해 list comprehension 사용)
        rotated = [list(x) for x in zip(*shape[::-1])]
        # 회전 후 벽을 벗어나지 않는지 검사 후 적용
        if not check_collision(r, c, rotated):
            st.session_state.current_shape = rotated

# 세션 상태가 비어있다면 최초 1회 초기화
if 'board' not in st.session_state:
    init_game()

# --- 화면 렌더링 영역 ---
st.title("🧱 에러 없는 스트림릿 테트리스")
st.write(f"### 🏆 현재 점수: **{st.session_state.score}** 점")

if st.session_state.game_over:
    st.error("🚨 GAME OVER! 블록이 가득 찼습니다.")
    if st.button("다시 시작하기", type="primary"):
        init_game()
        st.title("다시 시작 중...") # 리런 유도용 임시 렌더링
        st.rerun()

# 출력용 임시 게임판 복사
display_board = [row[:] for row in st.session_state.board]

# 현재 조작 중인 블록을 보드 위에 합성 (게임오버가 아닐 때만)
if not st.session_state.game_over:
    r = st.session_state.block_row
    c = st.session_state.block_col
    shape = st.session_state.current_shape
    for i in range(len(shape)):
        for j in range(len(shape[i])):
            if shape[i][j]:
                if 0 <= (r + i) < GRID_ROWS and 0 <= (c + j) < GRID_COLS:
                    display_board[r + i][c + j] = 2  # 조작중인 블록은 숫자 2로 세팅

# 보드판을 이모지 문자열로 변환하여
