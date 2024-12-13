import pygame
import os
import random

# Pygame 초기화
pygame.init()

# 사운드 믹서 초기화
pygame.mixer.init()

# 화면 크기 설정
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("플레이어와 보스의 대결")

# 배경음악 추가
try:
    pygame.mixer.music.load('게임,보스-1.ogg')  # 배경음악 파일 경로 설정
    pygame.mixer.music.set_volume(0.5)  # 볼륨 설정 (0.0 ~ 1.0)
    pygame.mixer.music.play(-1)  # 무한 반복 재생
except pygame.error as e:
    print(f"음악 파일을 로드할 수 없습니다: {e}")

# 색상 설정
BUTTON_COLOR = (139, 69, 19)  # 기본 버튼 색상: 갈색
BUTTON_HOVER_COLOR = (160, 82, 45)  # 마우스 오버 시 버튼 색상
TEXT_COLOR = (255, 255, 255)
PARAO_COLOR = (255, 0, 0)
RED_SCREEN_COLOR = (255, 0, 0)  # 빨간색
HP_BAR_COLOR = (0, 225, 0)  # HP 바 색상: 초록
KING_COLOR = (255, 0, 0)

# 폰트 설정 (Windows 시스템에서 기본 제공되는 Malgun Gothic)
try:
    font = pygame.font.SysFont("malgungothic", 36)
except FileNotFoundError:
    print("Malgun Gothic 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
    font = pygame.font.Font(None, 36)

# 이미지 로드
player_image = pygame.image.load('image/boss/boss_player.png')
player_image = pygame.transform.scale(player_image, (130, 130))

player_hit_image = pygame.image.load('image/boss/보스플레이어_맞는모습.png')  # 플레이어 피격 이미지
player_hit_image = pygame.transform.scale(player_hit_image, (150, 150))  # 크기 맞추기

boss_image = pygame.image.load('image/boss/boss.png')
boss_image = pygame.transform.scale(boss_image, (300, 300))

boss_hit_image = pygame.image.load('image/boss/보스_공격모습.png')  # 보스 공격 이미지
boss_hit_image = pygame.transform.scale(boss_hit_image, (300, 300))  # 보스 공격 이미지 크기 조정

background_image = pygame.image.load('image/boss/boss_background.png')
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

# 하트 이미지 로드
heart_image = pygame.image.load("image/boss/playerheart1.png")  # 플레이어 하트 이미지 파일 경로
heart_image = pygame.transform.scale(heart_image, (22, 22))  # 플레이어 하트 크기 조정

# 보스 하트 이미지 로드 (보스 전용 하트 이미지)
boss_heart_image = pygame.image.load("image/boss/bossheart1.png")  # 보스 하트 이미지 파일 경로
boss_heart_image = pygame.transform.scale(boss_heart_image, (22, 22))  # 보스 하트 크기 조정

# 빈 하트 이미지 로드
empty_heart_image = pygame.image.load("image/boss/bossheart2.png")  # 빈 하트 이미지 파일 경로
empty_heart_image = pygame.transform.scale(empty_heart_image, (22, 22))  # 빈 하트 크기 조정

# 플레이어 이동 시 사용할 이미지
player_up_image = pygame.image.load('image/boss/보스플레이어_공격하는모습.png')  # 위로 이동하는 이미지
player_up_image = pygame.transform.scale(player_up_image, (150, 150))

player_down_image = pygame.image.load('image/boss/보스플레이어_공격하는모습.png')  # 아래로 이동하는 이미지
player_down_image = pygame.transform.scale(player_down_image, (150, 150))

# 플레이어의 현재 이동 이미지 변수
current_player_image = player_image  # 기본 이미지로 시작

# 플레이어와 보스의 초기 상태
player_hp = 20
boss_hp = 25
player_damage = 1  # 기본 공격력
boss_damage = 1  # 기본 보스 공격력

# 플레이어 위치
player_x = 20
player_y = 220
player_move_speed = 10
player_move_up = False
is_player_moving = False

# 라인 설정
line_1 = "라인1"
line_2 = "라인2"
selected_line = None
boss_line = None

# 피격 효과 설정
hit_effect_active = False
hit_effect_timer = 0
hit_effect_duration = 500  # 효과 지속 시간 (밀리초)

# 보스 등장 시간 설정
boss_appears_time = None  # 보스 등장 시각
boss_appeared = False  # 보스가 등장했는지 여부

# 흔들림 효과 관련 변수
shake_active = False  # 흔들림 효과 활성화 여부
shake_start_time = 0  # 흔들림 시작 시간
shake_duration = 3000  # 흔들림 지속 시간 (3초)
shake_intensity = 10  # 흔들림 강도 (픽셀)
shake_offset_x = 0  # x축 방향 흔들림
shake_offset_y = 0  # y축 방향 흔들림

# 쿨다운 설정
last_selection_time = 0  # 마지막 라인 선택 시간
line_selection_cooldown = 1000  # 쿨다운 시간 1초 (1000ms)

# 이미지 버튼을 위한 새로운 클래스
class Button:
    def __init__(self, x, y, width, height, image, action=None, enabled=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.transform.scale(image, (width, height))  # 버튼 크기 조정
        self.action = action
        self.enabled = enabled  # 버튼 활성화 여부

    def draw(self, screen):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.enabled:
            if self.rect.collidepoint(mouse_x, mouse_y):
                # 마우스 오버 시 색상 변화 (Hover 효과)
                screen.blit(self.image, (self.rect.x, self.rect.y))  # 이미지로 버튼을 그린다.
            else:
                screen.blit(self.image, (self.rect.x, self.rect.y))  # 일반 상태에서 버튼 그리기
        else:
            # 비활성화된 버튼은 회색으로 표시 (이미지 대신 회색 박스)
            pygame.draw.rect(screen, (100, 100, 100), self.rect)
        
    def is_clicked(self, mouse_pos):
        if self.enabled and self.rect.collidepoint(mouse_pos):
            if self.action:
                self.action()

# 라인 선택 함수 (플레이어)
def choose_line_for_player(line):
    global selected_line, is_player_moving, player_move_up, last_selection_time
    current_time = pygame.time.get_ticks()

    # 쿨다운 체크: 마지막 선택 후 일정 시간이 지나야 다시 선택 가능
    if current_time - last_selection_time >= line_selection_cooldown:
        selected_line = line
        last_selection_time = current_time  # 마지막 선택 시간 갱신
        if line == line_1:
            player_move_up = True
        elif line == line_2:
            player_move_up = False
        is_player_moving = True

# 보스 라인 선택 함수
def choose_line_for_boss():
    global boss_line
    boss_line = random.choice([line_1, line_2])

# 공격 함수
def player_attack():
    damage = player_damage
    return damage

def boss_attack(selected_line, boss_line):
    global hit_effect_active  # 피격 효과 활성화 상태
    damage = 0
    if selected_line == boss_line:
        damage = boss_damage
        hit_effect()  # 보스의 공격이 맞았을 때 피격 효과를 활성화
    return damage

# 보스의 상태에 따른 데미지 조정 및 메시지 출력
def check_boss_status():
    global boss_damage, boss_hp
    if boss_hp <= 10 and boss_damage == 1:  # 보스 HP가 10 이하일 때
        boss_damage = 2  # 보스 데미지 증가
        show_boss_rage_message()  # "파라오의 분노가 느껴집니다." 메시지 출력

# 보스의 분노 메시지 출력 함수
def show_boss_rage_message():
    rage_text = font.render("파라오의 분노가 느껴집니다.", True, PARAO_COLOR)
    rage_rect = rage_text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(rage_text, rage_rect)
    pygame.display.update()
    pygame.time.delay(1500)  # 1.5초 동안 메시지 표시

# 피격 효과 함수
def hit_effect():
    global hit_effect_active, hit_effect_timer
    hit_effect_timer = pygame.time.get_ticks()  # 피격 시간을 기록
    hit_effect_active = True  # 피격 효과 활성화

# 화면에 빨간 레이어 그리기 (피격 효과)
def draw_red_screen_overlay():
    red_overlay = pygame.Surface((screen_width, screen_height))
    red_overlay.fill(RED_SCREEN_COLOR)
    red_overlay.set_alpha(30)  # 30% 투명도
    screen.blit(red_overlay, (0, 0))  # 빨간 레이어를 화면에 덮기

# 하트 이미지로 체력 표시 함수 (플레이어용 하트)
def draw_heart_health(x, y, hp, max_hp, is_player=True, heart_spacing=35):
    heart_image_to_use = heart_image if is_player else boss_heart_image  # 플레이어 또는 보스 하트 선택
    empty_heart_image_to_use = empty_heart_image if is_player else empty_heart_image  # 빈 하트 선택
    hearts_per_row = 10  # 한 줄에 표시할 최대 하트 개수
    rows = (max_hp + hearts_per_row - 1) // hearts_per_row  # 필요한 행 수 계산
    
    for row in range(rows):
        for i in range(min(hearts_per_row, max_hp - row * hearts_per_row)):
            # 남은 체력만큼 채운 하트를 표시하고, 나머지는 빈 하트 표시
            if i < hp - row * hearts_per_row:
                screen.blit(heart_image_to_use, (x + i * heart_spacing, y + row * heart_spacing))  # 채워진 하트
            else:
                screen.blit(empty_heart_image_to_use, (x + i * heart_spacing, y + row * heart_spacing))  # 빈 하트

# 게임 재시작 버튼
def restart_game():
    global player_hp, boss_hp, boss_appeared, shake_active, shake_start_time, player_hit
    player_hp = 20
    boss_hp = 30
    boss_appeared = False  # 보스를 다시 등장하지 않도록 설정
    shake_active = False  # 흔들림 효과 비활성화
    shake_start_time = 0  # 흔들림 시작 시간 초기화
    player_hit = False  # 피격 상태 해제

# 게임 시작 시 스토리 텍스트
def start_game_story():
    start_text = font.render("무슨 일이 발생하고 있습니다....!", True, TEXT_COLOR)
    start_rect = start_text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(start_text, start_rect)
    pygame.display.update()
    pygame.time.delay(2000)  # 2초 동안 텍스트 표시 후 시작

# 게임 종료 시 스토리 텍스트
def display_end_story(winner):
    if winner == "player":
        end_text = font.render("당신은 파라오의 저주로부터 살아남았습니다!", True, HP_BAR_COLOR)
    elif winner == "boss":
        end_text = font.render("당신은 파라오의 저주에 빠졌습니다!!!!", True, PARAO_COLOR)
    end_rect = end_text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(end_text, end_rect)
    pygame.display.update()
    pygame.time.delay(2000)  # 2초 동안 텍스트 표시 후 게임 재시작

# 화면 흔들림 효과 함수
def shake_screen():
    global shake_active, shake_start_time, shake_duration, shake_offset_x, shake_offset_y
    if shake_active:
        current_time = pygame.time.get_ticks()
        if current_time - shake_start_time < shake_duration:  # 흔들림 지속 시간 동안
            shake_offset_x = random.randint(-shake_intensity, shake_intensity)
            shake_offset_y = random.randint(-shake_intensity, shake_intensity)
            return True  # 흔들림 효과를 계속 활성화
        else:
            shake_active = False  # 흔들림 종료
            return False
    return False


# 이미지 파일 경로에 맞는 이미지를 불러옵니다.
line1_image = pygame.image.load("image/boss/line1btn1.png")  # line1 이미지 버튼
line2_image = pygame.image.load("image/boss/line2btn1.png")  # line2 이미지 버튼

# 게임 루프
running = True

# 버튼 객체 생성
line1_button = Button(150, screen_height - 100, 200, 85, line1_image, lambda: choose_line_for_player(line_1), enabled=False)
line2_button = Button(screen_width - 350, screen_height - 100, 200, 85, line2_image, lambda: choose_line_for_player(line_2), enabled=False)

# 게임 시작 시 스토리 텍스트 출력
start_game_story()

# 보스 등장 시간을 설정 (게임 시작 후 3초 뒤에 등장)
boss_appears_time = pygame.time.get_ticks() + 3000  # 3초 후 보스 등장
line_buttons_available_time = pygame.time.get_ticks() + 6000  # 3초 후 라인 버튼 활성화

while running:
    current_time = pygame.time.get_ticks()  # 현재 시간
    choose_line_for_boss()  # 보스 라인 선택

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            line1_button.is_clicked(mouse_pos)
            line2_button.is_clicked(mouse_pos)

    # 3초 후 라인 버튼을 활성화
    if current_time >= line_buttons_available_time:
        line1_button.enabled = True
        line2_button.enabled = True

    # 보스 등장 처리
    if not boss_appeared and current_time >= boss_appears_time:
        boss_appeared = True  # 보스가 등장했음을 표시
        shake_active = True  # 보스가 등장할 때 흔들림 효과 활성화
        shake_start_time = current_time  # 흔들림 시작 시간 기록

    # 화면 흔들림 처리
    if shake_screen():
        pass  # 흔들림 효과가 진행 중이면 아무 작업도 하지 않음

    # 플레이어 이동
    if is_player_moving:
        if player_move_up:
            player_y -= player_move_speed
            current_player_image = player_up_image  # 위로 이동할 때 이미지를 변경
            if player_y <= 10:
                player_y = 100
                is_player_moving = False
                current_player_image = player_image  # 이동이 끝났을 때 원래 이미지로 되돌리기
        else:
            player_y += player_move_speed
            current_player_image = player_down_image  # 아래로 이동할 때 이미지를 변경
            if player_y >= screen_height - 300:
                player_y = screen_height - 370
                is_player_moving = False
                current_player_image = player_image  # 이동이 끝났을 때 원래 이미지로 되돌리기

    # 공격 처리 (이제 이동이 끝난 후에만 처리)
    if selected_line and not is_player_moving:
        boss_hp -= player_attack()
        if boss_hp <= 0:
            display_end_story("player")
            restart_game()
            break

        player_hp -= boss_attack(selected_line, boss_line)
        if player_hp <= 0:
            display_end_story("boss")
            restart_game()
            break

        selected_line = None

    # 보스 상태 체크 (보스 체력 10 이하에서 데미지 증가 및 메시지 출력)
    check_boss_status()

    # 피격 효과가 일정 시간 후 사라지도록
    if hit_effect_active and current_time - hit_effect_timer > hit_effect_duration:
        hit_effect_active = False  # 피격 효과 종료

    # 화면 그리기
    screen.blit(background_image, (0, 0))

    # 플레이어와 보스의 HP를 하트로 표시
    draw_heart_health(30, 30, player_hp, 20, is_player=True, heart_spacing=20)  # 하트 간격을 20으로 조정
    draw_heart_health(screen_width - 230, 30, boss_hp, 25, is_player=False, heart_spacing=20)  # 보스도 동일

    # 화면 흔들림을 고려한 플레이어 위치 업데이트
    if hit_effect_active:
        screen.blit(player_hit_image, (player_x + shake_offset_x, player_y + shake_offset_y))  # 피격 이미지 표시
    else:
        screen.blit(current_player_image, (player_x + shake_offset_x, player_y + shake_offset_y))  # 이동 이미지 표시

    # 보스가 등장한 경우에만 보스를 화면에 표시
    if boss_appeared:
        if hit_effect_active:
            screen.blit(boss_hit_image, (500 + shake_offset_x, 100 + shake_offset_y))  # 보스 피격 이미지 표시
        else:
            screen.blit(boss_image, (500 + shake_offset_x, 100 + shake_offset_y))  # 보스 이미지 표시

    # 라인 버튼 그리기
    line1_button.draw(screen)
    line2_button.draw(screen)

    # 피격 효과 시 빨간 화면 레이어 추가
    if hit_effect_active:
        draw_red_screen_overlay()

    # "PLAYER"와 "BOSS" 문구 화면에 출력
    player_text = font.render("PLAYER", True, TEXT_COLOR)
    boss_text = font.render("BOSS", True, TEXT_COLOR)
    
    # "PLAYER"를 왼쪽 하단에 표시
    screen.blit(player_text, (30, screen_height - 40))
    
    # "BOSS"를 오른쪽 하단에 표시
    screen.blit(boss_text, (screen_width - 180, screen_height - 40))

    # 게임 화면 업데이트
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()

'''끝'''