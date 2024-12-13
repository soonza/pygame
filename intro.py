import pygame
import sys
import os
import subprocess

# 초기화
pygame.init()

# 화면 크기 설정
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("파이게임 인트로")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HELP = (250,237,125)

# 폰트 설정
font_path = pygame.font.match_font("malgun gothic")  # 시스템에서 '맑은 고딕' 찾기
font = pygame.font.Font(font_path, 20)

# 이미지 로드 함수
def load_image(path, size=None):
    try:
        image = pygame.image.load(path)
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except pygame.error:
        print(f"이미지 {path}를 찾을 수 없습니다!")
        sys.exit()

# 이미지 로드
background_img = load_image("image/intro/intro_background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
start_button_img = load_image("image/intro/start_icon.png", (200, 80))
quit_button_img = load_image("image/intro/quit_icon.png", (200, 80))
help_button_img = load_image("image/intro/help_icon.png", (200, 75))

# 버튼 좌표 및 크기
buttons = {
    "start": {"image": start_button_img, "rect": pygame.Rect(295, 480, 200, 80)},
    "help": {"image": help_button_img, "rect": pygame.Rect(80, 483, 200, 80)},
    "quit": {"image": quit_button_img, "rect": pygame.Rect(510, 480, 200, 80)},
}

# 버튼 호버 효과 함수
def button_hover_effect(button_rect, original_img, hover_img):
    if button_rect.collidepoint(pygame.mouse.get_pos()):
        screen.blit(hover_img, button_rect.topleft)
    else:
        screen.blit(original_img, button_rect.topleft)

# 게임 설명 창
def show_help():
    help_background_img = load_image("image/intro/help_background.png", (800, 400))
    help_screen = pygame.display.set_mode((800, 400))
    pygame.display.set_caption("Game Help")

    running = True
    while running:
        help_screen.blit(help_background_img, (0, 0))

        # 텍스트 표시
        help_text_lines = [
            "게임 설명:",
            "플레이어는 고대 피라미드의 도굴꾼이 되어", 
            "4가지의 시련을 헤쳐나가고 보물을 얻는 것이 최종 목표입니다.",
            "",
            "1.미로게임: 방향키(←→↑↓)를 이용하여 출구를 찾아 탈출하세요!",
            "",
            "2.퀴즈게임: 스핑크스가 내는 퀴즈를 풀어 제한된 목숨 안에서 생존하세요!",
            "",
            "3.블록낙하게임: 하늘에서 블록이 떨어집니다. 방향키(←→) 및",
            "스페이스바 버튼으로 블록을 피하고 생존하세요!",
            "",
            "4. 보스게임: 마지막 게임은 보스게임입니다. 라인1과2 중",
            "하나를 골라 보스와의 전투에서 생존하고 보물을 탈취하세요!",
        ]
        for i, line in enumerate(help_text_lines):
            text_surface = font.render(line, True, HELP)
            help_screen.blit(text_surface, (10, 30 + i * 25))

        back_text = font.render("ESC를 눌러 돌아가기", True, HELP)
        help_screen.blit(back_text, (30, 370))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # 인트로 화면 복구

# 인트로 화면
def show_intro():
    running = True
    while running:
        screen.blit(background_img, (0, 0))

        for button in buttons.values():
            screen.blit(button["image"], button["rect"].topleft)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 왼쪽 클릭
                mouse_pos = pygame.mouse.get_pos()
                if buttons["start"]["rect"].collidepoint(mouse_pos):
                    if not os.path.exists("maze1.py"):
                        print("maze1.py 파일이 없습니다!")
                        sys.exit()
                    pygame.quit()  # 현재 인트로 화면 종료
                    subprocess.run([sys.executable, "maze1.py"])  # maze1.py 실행
                    sys.exit()
                elif buttons["help"]["rect"].collidepoint(mouse_pos):
                    show_help()
                elif buttons["quit"]["rect"].collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

# 실행 테스트
if __name__ == "__main__":
    show_intro()
