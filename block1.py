import pygame
import random
import sys

# 색상 정의
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# 화면 크기 및 설정
WIDTH, HEIGHT = 800, 800
TILE_SIZE = WIDTH // 8
HEALTH = 20  # 플레이어 초기 목숨

# pygame 초기화
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("파이게임 블록낙하1")
clock = pygame.time.Clock()
FPS = 60

# 음악 초기화
pygame.mixer.init()
pygame.mixer.music.load("block_bgm.mp3")  # 배경 음악 파일 로드
pygame.mixer.music.play(-1)  # 반복 재생

# 이미지 로드
background = pygame.transform.scale(pygame.image.load("image/block/BlockGamebg.png"), (WIDTH, HEIGHT))

# 블록 이미지 로드
blockFall = pygame.transform.scale(pygame.image.load("image/block/blockFall.png"), (TILE_SIZE, TILE_SIZE))
blockFall2 = pygame.transform.scale(pygame.image.load("image/block/blockFall2.png"), (2 * TILE_SIZE, TILE_SIZE))
blockFall3 = pygame.transform.scale(pygame.image.load("image/block/blockFall3.png"), (3 * TILE_SIZE, TILE_SIZE))
blockFall4 = pygame.transform.scale(pygame.image.load("image/block/blockFall4.png"), (4 * TILE_SIZE, TILE_SIZE))

# 체력(하트) 이미지 로드
full_heart = pygame.transform.scale(pygame.image.load("image/block/fullhp.png"), (20, 20))
empty_heart = pygame.transform.scale(pygame.image.load("image/block/minushp.png"), (20, 20))

# 플레이어 애니메이션 이미지 로드
player_walk_right = [pygame.image.load(f"image/block/right0{i}.png") for i in range(1, 9)]
player_walk_left = [pygame.transform.flip(image, True, False) for image in player_walk_right]
player_jump_images = [
    pygame.image.load("image/block/jump1.png"),
    pygame.image.load("image/block/jump2.png"),
    pygame.image.load("image/block/jump3.png"),
    pygame.image.load("image/block/jump4.png")
]
idle_image = player_walk_right[0]

# AnimatedSprite 클래스 정의
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.images_right = player_walk_right
        self.images_left = player_walk_left
        self.images_idle = [pygame.image.load("image/block/stop.png")]  # stop.png 이미지
        self.images_jump = player_jump_images

        self.images = self.images_idle
        self.index = 0
        self.image = self.images[self.index]

        self.rect = self.image.get_rect()
        self.rect.topleft = position

        self.animation_time = 0.1
        self.current_time = 0

        self.state = "idle"
        self.direction = "right"
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_jumping = False

    def update(self, dt):
        keys = pygame.key.get_pressed()

        # 키 입력이 없을 때 idle 상태로 설정
        if not keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT] and not self.is_jumping:
            self.state = "idle"

        # 상태에 따른 이미지 선택
        if self.is_jumping:
            self.images = self.images_jump
        elif self.state == "moving":
            self.images = self.images_right if self.direction == "right" else self.images_left
        else:
            self.images = self.images_idle

        # 애니메이션 업데이트
        self.current_time += dt
        if self.current_time >= self.animation_time:
            self.current_time = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

        # 위치 업데이트
        self.rect.x += self.velocity_x
        self.rect.x = max(0, min(self.rect.x, WIDTH - TILE_SIZE))

        # 점프 처리
        if self.is_jumping:
            self.rect.y += self.velocity_y
            self.velocity_y += 0.5  # 중력 효과
            if self.rect.y >= HEIGHT - TILE_SIZE:
                self.rect.y = HEIGHT - TILE_SIZE
                self.is_jumping = False
                self.state = "idle"

# 초기화
player = AnimatedSprite(position=(WIDTH // 2, HEIGHT - TILE_SIZE))
all_sprites = pygame.sprite.Group(player)
block_falls = []
health = HEALTH
start_time = pygame.time.get_ticks()
running = True  # 게임 루프 실행 플래그 추가
last_spawn_time = 0  # 마지막 블록 생성 시간

# 블록 생성 함수
def spawn_block_fall():
    num_blocks = random.randint(1, 3)  # 1~3개의 블록 생성
    for _ in range(num_blocks):
        choice = random.randint(1, 4)  # 블록 종류 선택
        x = random.randint(0, WIDTH - TILE_SIZE)
        speed = random.randint(5, 10)
        if choice == 1:
            block_falls.append({"rect": pygame.Rect(x, 0, TILE_SIZE, TILE_SIZE), "image": blockFall, "speed": speed})
        elif choice == 2:
            block_falls.append({"rect": pygame.Rect(x, 0, 2 * TILE_SIZE, TILE_SIZE), "image": blockFall2, "speed": speed})
        elif choice == 3:
            block_falls.append({"rect": pygame.Rect(x, 0, 3 * TILE_SIZE, TILE_SIZE), "image": blockFall3, "speed": speed})
        elif choice == 4:
            block_falls.append({"rect": pygame.Rect(x, 0, 4 * TILE_SIZE, TILE_SIZE), "image": blockFall4, "speed": speed})

# 블록 이동 및 충돌 처리
def draw_block_falls():
    global health
    for block in block_falls[:]:
        block["rect"].y += block["speed"]
        if block["rect"].colliderect(player.rect):
            health -= 1  # 충돌 시 체력 감소
            block_falls.remove(block)
        elif block["rect"].y > HEIGHT:
            block_falls.remove(block)  # 화면 밖으로 나간 블록 제거
        else:
            screen.blit(block["image"], block["rect"])

# 하트로 체력 표시
def draw_health():
    for i in range(HEALTH):
        x = WIDTH - ((i % 10) * 22) - 22
        y = 10 if i < 10 else 35
        if i < health:
            screen.blit(full_heart, (x, y))
        else:
            screen.blit(empty_heart, (x, y))

# 타이머 표시
def draw_timer(timer):
    font = pygame.font.Font(None, 36)
    timer_text = font.render(f"Time: {timer}s", True, WHITE)
    screen.blit(timer_text, (10, 40))

# 게임 루프
while running:
    dt = clock.tick(FPS) / 1000
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        player.state = "moving"
        player.direction = "right"
        player.velocity_x = 5
    elif keys[pygame.K_LEFT]:
        player.state = "moving"
        player.direction = "left"
        player.velocity_x = -5
    else:
        player.velocity_x = 0

    if keys[pygame.K_SPACE] and not player.is_jumping:
        player.is_jumping = True
        player.state = "jumping"
        player.velocity_y = -15

    # 블록 생성
    if pygame.time.get_ticks() - last_spawn_time >= 2000:  # 2초마다 블록 생성
        spawn_block_fall()
        last_spawn_time = pygame.time.get_ticks()

    # 타이머 업데이트
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    timer = 60 - elapsed_time
    if timer <= 0 or health <= 0:
        running = False

    # 그리기
    draw_block_falls()
    draw_health()
    draw_timer(timer)
    all_sprites.update(dt)
    all_sprites.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
