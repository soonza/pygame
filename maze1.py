import pygame
import sys
import random
import math
import time
import subprocess

# 초기화
pygame.init()
pygame.mixer.init()

# 음악 파일 로드
music_path = "maze_bgm.mp3"
try:
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print(f"음악 로드 실패: {e}")

# 화면 크기와 타일 크기 설정
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
TILE_SIZE = 50
PLAYER_SIZE = TILE_SIZE // 2
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("파이게임 미로")

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# 폰트 설정
font_path = pygame.font.match_font("malgun gothic")
font = pygame.font.Font(font_path, 24)

# 이미지 로드
def load_image(path, fallback_color=None, size=None):
    try:
        image = pygame.image.load(path)
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except pygame.error:
        if fallback_color:
            surface = pygame.Surface(size or (TILE_SIZE, TILE_SIZE))
            surface.fill(fallback_color)
            return surface
        return None

wall_img = load_image("image/maze/wall.png", (0, 0, 0), (TILE_SIZE, TILE_SIZE))
path_img = load_image("image/maze/path.png", (255, 255, 255), (TILE_SIZE, TILE_SIZE))
exit_img = load_image("image/maze/exit.png", (0, 255, 0), (TILE_SIZE, TILE_SIZE))

player_images = {
    "back": [load_image(f"image/maze/player/back{i}.png") for i in range(1, 7)],
    "front": [load_image(f"image/maze/player/front{i}.png") for i in range(1, 7)],
    "left": [load_image(f"image/maze/player/left{i}.png") for i in range(1, 7)],
    "right": [load_image(f"image/maze/player/right{i}.png") for i in range(1, 7)],
    "stop": [load_image("image/maze/player/stop.png")],
}

# 충돌 검사 함수 개선
def is_walkable_rect(x, y):
    """
    플레이어가 이동하려는 위치에서 충돌을 확인.
    이미지 경계와 타일의 충돌 여부를 검사.
    """
    # 플레이어의 이미지 크기를 기반으로 정확한 경계를 설정
    player_width, player_height = PLAYER_SIZE, int(PLAYER_SIZE * 1.8)  # 다리 포함 크기 조정
    corners = [
        (x, y),  # 왼쪽 위
        (x + player_width - 1, y),  # 오른쪽 위
        (x, y + player_height - 1),  # 왼쪽 아래
        (x + player_width - 1, y + player_height - 1),  # 오른쪽 아래
    ]
    
    for corner_x, corner_y in corners:
        tile_x = corner_x // TILE_SIZE
        tile_y = corner_y // TILE_SIZE
        if 0 <= tile_y < len(maze) and 0 <= tile_x < len(maze[0]):
            if maze[tile_y][tile_x] == 1:  # 벽 타일
                return False
        else:
            return False  # 미로 범위를 벗어나면 이동 불가
    return True


# 거리 기반 밝기 효과
def apply_distance_brightness(screen_x, screen_y, col, row):
    player_screen_x = (player_x - camera_x) + TILE_SIZE // 2
    player_screen_y = (player_y - camera_y) + TILE_SIZE // 2
    tile_center_x = screen_x + TILE_SIZE // 2
    tile_center_y = screen_y + TILE_SIZE // 2
    distance = math.sqrt((tile_center_x - player_screen_x) ** 2 +
                         (tile_center_y - player_screen_y) ** 2)

    if distance > MAX_VIEW_DISTANCE:
        alpha = 255  # 너무 멀면 완전히 어둡게
    else:
        alpha = int(255 * (distance / MAX_VIEW_DISTANCE))  # 가까울수록 밝게

    overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    screen.blit(overlay, (screen_x, screen_y))

# 타이머 그리기
def draw_timer():
    elapsed_time = time.time() - start_time
    remaining_time = max(0, stage_time_limit - elapsed_time)
    timer_text = font.render(f"남은 시간: {int(remaining_time)}초", True, WHITE)
    screen.blit(timer_text, (10, 10))
    return remaining_time

# 스크립트 실행 후 다음 스테이지 시작
def handle_stage_completion(stage):
    """스테이지 완료 시 외부 스크립트 실행 후 maze1.py 재시작."""
    pygame.quit()  # Pygame 환경 종료

    if stage == 1:
        scripts = ["block1.py", "quiz1.py"]
    elif stage == 2:
        scripts = ["block2.py", "quiz2.py"]
    elif stage == 3:
        subprocess.run([sys.executable, "boss_battle.py"])
        sys.exit()

    # 랜덤 스크립트 실행
    chosen_script = random.choice(scripts)
    result = subprocess.run([sys.executable, chosen_script])

    # 외부 스크립트 실패 시 maze1.py도 종료
    if result.returncode != 0:  # 비정상 종료
        print(f"{chosen_script} 실패: maze1.py 종료")
        sys.exit()

    # maze1.py 재시작 (다음 스테이지)
    subprocess.run([sys.executable, sys.argv[0], str(stage)])
 
    sys.exit()  # 종료
# 미로 생성 함수
def generate_maze(rows, cols):
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    stack = [(1, 1)]
    maze[1][1] = 0
    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
    while stack:
        cx, cy = stack[-1]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 < nx < rows - 1 and 0 < ny < cols - 1 and maze[nx][ny] == 1:
                maze[(cx + nx) // 2][(cy + ny) // 2] = 0
                maze[nx][ny] = 0
                stack.append((nx, ny))
                break
        else:
            stack.pop()
    exit_candidates = [(1, cols - 2), (rows - 2, 1), (rows - 2, cols - 2)]
    ex, ey = random.choice(exit_candidates)
    maze[ex][ey] = 2
    return maze

# 초기 설정
stages = [(15, 15), (25, 25), (35, 35)]
STAGE_TIME_LIMITS = [60, 90, 120]
current_stage = int(sys.argv[1]) if len(sys.argv) > 1 else 0
maze = generate_maze(*stages[current_stage])
player_x, player_y = TILE_SIZE, TILE_SIZE
camera_x, camera_y = 0, 0
player_speed = 5
MAX_VIEW_DISTANCE = 200
start_time = time.time()
stage_time_limit = STAGE_TIME_LIMITS[current_stage]

# 애니메이션 변수
player_direction = "stop"
animation_index = 0
animation_delay = 5
animation_counter = 0

# 메인 루프
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    new_x, new_y = player_x, player_y
    if keys[pygame.K_UP]:
        player_direction = "back"
        new_y -= player_speed
    elif keys[pygame.K_DOWN]:
        player_direction = "front"
        new_y += player_speed
    elif keys[pygame.K_LEFT]:
        player_direction = "left"
        new_x -= player_speed
    elif keys[pygame.K_RIGHT]:
        player_direction = "right"
        new_x += player_speed
    else:
        player_direction = "stop"

    if player_direction == "stop":
        animation_index = 0
    elif player_direction in player_images and len(player_images[player_direction]) > 0:
        animation_counter += 1
        if animation_counter >= animation_delay:
            animation_counter = 0
            animation_index = (animation_index + 1) % len(player_images[player_direction])
    if is_walkable_rect(new_x, player_y):
        player_x = new_x
    if is_walkable_rect(player_x, new_y):
        player_y = new_y
    camera_x = player_x - SCREEN_WIDTH // 2 + PLAYER_SIZE // 2
    camera_y = player_y - SCREEN_HEIGHT // 2 + PLAYER_SIZE // 2
    screen.fill(BLACK)
    for row in range(len(maze)):
        for col in range(len(maze[0])):
            screen_x = col * TILE_SIZE - camera_x
            screen_y = row * TILE_SIZE - camera_y
            if maze[row][col] == 1:
                screen.blit(wall_img, (screen_x, screen_y))
            elif maze[row][col] == 0:
                screen.blit(path_img, (screen_x, screen_y))
            elif maze[row][col] == 2:
                screen.blit(exit_img, (screen_x, screen_y))
            apply_distance_brightness(screen_x, screen_y, col, row)
    remaining_time = draw_timer()
    if remaining_time <= 0:
        print("시간 초과! 게임 오버!")
        running = False
    player_screen_x = player_x - camera_x
    player_screen_y = player_y - camera_y
    current_image = player_images[player_direction][animation_index]
    screen.blit(current_image, (player_screen_x, player_screen_y))
    player_tile_x = player_x // TILE_SIZE
    player_tile_y = player_y // TILE_SIZE
    if maze[player_tile_y][player_tile_x] == 2:
        current_stage += 1
        handle_stage_completion(current_stage)
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
