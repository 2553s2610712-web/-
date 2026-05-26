import streamlit as st
import numpy as np
import time

# 기본 페이지 설정 및 스타일 주입 (버튼 클릭 시 화면 흔들림 방지)
st.set_page_config(page_title="스트림릿 테트리스", layout="centered")
st.markdown("""
    <style>
    div.stButton > button { width: 100%; margin-bottom: 5px; }
    .block-container { padding-top: 2rem; }
    </style>
""", unsafe_allow_html=True)

# 게임판 크기 정의
GRID_ROWS = 20
GRID_COLS = 10

# 테트로미노(블록) 모양 정의
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]]
}

# 💡 1. 게임 상태 초기화 함수
def init_game():
    st.session_state.board = np.zeros((GRID_ROWS, GRID_COLS), dtype=int)
    st.session_state.score = 0
    st.session_state.game_over = False
    spawn_block()

# 블록 새로 생성
def spawn_block():
    shape_names = list(SHAPES.keys())
    # 2026년 기준 Streamlit 호환 안전한 난수 생성
    np.random.seed(int(time.time() * 1000) % 2**32)
    chosen = np.random.choice(shape_names)
    st.session_state.current_shape = SHAPES[chosen]
    st.session_state.block_row = 0
    st.session_state.block_col = GRID_COLS // 2 - len(st.session_state.current_shape[0]) // 2
    
    if check_collision(st.session_state.block_row, st.session_state.block_col, st.session_state.current_shape):
        st.session_state.game_over = True

# 💡 2. 충돌 체크 함수 (벽, 바닥, 다른 블록)
def check_collision(r, c, shape):
    for i, row in enumerate(shape):
        for j, val in enumerate(row):
            if val:
                next_r = r + i
                next_c = c + j
                if next_r >= GRID_ROWS or next_c < 0 or next_c >= GRID_COLS:
                    return True
                if next_r >= 0 and st.session_state.board[next_r, next_c]:
                    return True
    return False

# 💡 3. 블록 고정 및 줄 지우기
def freeze_block():
    shape = st.session_state.current_shape
    r = st.session_state.block_row
    c = st.session_state.block_col
    for i, row in enumerate(shape):
        for j, val in enumerate(row):
            if val and (r + i) >= 0:
                st.session_state.board[r + i, c + j] = 1
                
    # 완성된 줄 지우기 및 점수 계산
    board = st.session_state.board
    non_full_rows = [row for row in board if not np.all(row)]
    cleared_lines = GRID_ROWS - len(non_full_rows)
    
    if cleared_lines > 0:
        new_board = np.zeros((cleared_lines, GRID_COLS), dtype=int)
        st.session_state.board = np.vstack([new_board, non_full_rows])
        st.session_state.score += cleared_lines * 100

    spawn_block()

# 💡 4. 블록 이동/회전 조작 함수
def move(direction):
    if st.session_state.game_over:
        return
    if direction == 'left':
        if not check_collision(st.session_state.block_row, st.session_state.block_col - 1, st.session_state.current_shape):
            st.session_state.block_col -= 1
    elif direction == 'right':
        if not check_collision(st.session_state.block_row, st.session_state.block_col + 1, st.session_state.current_shape):
            st.session_state.block_col += 1
    elif direction == 'down':
        if not check_collision(st.session_state.block_row + 1, st.session_state.block_col, st.session_state.current_shape):
            st.session_state.block_row += 1
        else:
            freeze_block()
    elif direction == 'rotate':
        rotated = np.rot90(st.session_state.current_shape, -1).tolist()
        if not check_collision(st.session_state.block_row, st.session_state.block_col, rotated):
            st.session_state.current_shape = rotated

# 세션 상태 초기화 실행
if 'board' not in st.session_state:
    init_game()

# --- UI 그리기 시작 ---
st.title("🧱 스트림릿 오리지널 테트리스")
st.write(f"### 현재 점수: **{st.session_state.score}** 점")

if st.session_state.game_over:
    st.error("🚨 GAME OVER! 블록이 끝까지 쌓였습니다.")
    if st.button("다시 시작하기", type="primary"):
        init_game()
        st.rerun()

# 💡 5. 현재 떨어지는 블록을 화면용 보드에 합성
display_board = st.session_state.board.copy()
if not st.session_state.game_over:
    shape = st.session_state.current_shape
    r = st.session_state.block_row
    c = st.session_state.block_col
    for i, row in enumerate(shape):
        for j, val in enumerate(row):
