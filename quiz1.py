import pygame
import random
import time

# 초기화
pygame.init()

# bgm 설정
pygame.display.set_caption("Pygame 사운드 출력")

# 화면 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("파이게임 퀴즈")

# 색상 설정
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
SAND = (194, 178, 128)
YELLOW = (255, 204, 0)
BLUE = (0, 0, 255)

# 폰트 설정
font = pygame.font.SysFont("malgungothic", 50)
big_font = pygame.font.SysFont("malgungothic", 65)
small_font = pygame.font.SysFont("malgungothic", 15)
result_font = pygame.font.SysFont("malgungothic",30)

# 하트 이미지 로드
heart_image = pygame.image.load('image/quiz/heart.png')
heart_image = pygame.transform.scale(heart_image, (30, 30))

# 빈 하트 이미지 로드
empty_heart_image = pygame.image.load('image/quiz/empty_heart.png')
empty_heart_image = pygame.transform.scale(empty_heart_image, (30, 30))

# 배경 이미지 로드
background_image = pygame.image.load('image/quiz/background.png')
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

#스핑크스 이미지 로드
sphinx_image = pygame.image.load('image/quiz/sphinx.png')
sphinx_image = pygame.transform.scale(sphinx_image, (330, 330))

# 플레이어 이미지 로드
player_image = pygame.image.load('image/quiz/player.png')
player_image = pygame.transform.scale(player_image, (200, 200))

# 문제 목록과 선택지 (각 문제에 대해 선택지 1번과 2번이 주어짐)
questions = [
    ("문제 1: 15 * 4는?", "60", "45"),
    ("문제 2: 13 + 8은?", "21", "25"),
    ("문제 3: 21 / 7은?", "3", "5"),
    ("문제 4: 16 - 7은?", "9", "5"),
    ("문제 5: 13 * 2은?", "26", "39")
]

# 하트 수 초기화
heart = 5

#bgm 로드
pygame.mixer.music.load("quiz_bgm.ogg")

# 퀴즈 진행 함수
def display_question(question, option1, option2, time_left, selected_option=None):
    global heart
    screen.fill(WHITE)

    # 배경 표시
    screen.blit(background_image, (0, 0))
    
    # 스핑크스 표시
    screen.blit(sphinx_image, (WIDTH - sphinx_image.get_width() - 5, 215))

    # 플레이어 표시
    screen.blit(player_image, (20, HEIGHT - player_image.get_height() - 65))
    
    # 하트 표시
    for i in range(5):
        if i < heart:
            screen.blit(heart_image, (20 + i * 40, 550))
        else:
            screen.blit(empty_heart_image, (20 + i * 40, 550))
    
    # 문제와 선택지 표시
    question_text = font.render(question, True, SAND)
    option1_text = font.render(f"① {option1}", True, RED)
    option2_text = font.render(f"② {option2}", True, RED)
    
    screen.blit(question_text, (20, 20))
    screen.blit(option1_text, (WIDTH // 2 - option1_text.get_width() // 2, 200))
    screen.blit(option2_text, (WIDTH // 2 - option1_text.get_width() // 2, 250))

    # 선택된 옵션 표시 (플레이어가 선택한 답안을 표시)
    if selected_option:
        # 선택된 답에 흰색 배경을 추가
        selected_text =result_font.render(f"선택한 답: {selected_option}", True, BLACK)
        text_width = selected_text.get_width()
        text_height = selected_text.get_height()
        
        # 흰색 배경 직사각형 그리기
        pygame.draw.rect(screen, WHITE, (WIDTH // 2 - text_width // 2 - 10, 440 - 10, text_width + 20, text_height + 20))
        
        # 선택한 답 텍스트 그리기
        screen.blit(selected_text, (WIDTH // 2 - selected_text.get_width() // 2, 440))
    # 제한시간 표시
    timer_text = font.render(f"Time: {time_left}s", True, YELLOW)
    screen.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 360))

    # BGM 정지 안내 메시지
    bgm_message1 = small_font.render("S: BGM정지", True, SAND)
    screen.blit(bgm_message1, (WIDTH // 2 - bgm_message1.get_width() // 2, HEIGHT - 40))

    pygame.display.update()

# 게임 시작 전 3초 동안 인트로 화면을 표시하는 함수
def intro_screen():
    screen.fill(BLACK)

    # "피라미드의 시련" 메시지 표시 (첫 번째 줄)
    intro_text_line1 = big_font.render("피라미드의 시련", True, SAND)
    screen.blit(intro_text_line1, (WIDTH // 2 - intro_text_line1.get_width() // 2, HEIGHT // 2 - intro_text_line1.get_height()))

    # "문제를 풀고" 메시지 표시 (두 번째 줄)
    intro_text_line2 = font.render("문제를 풀고", True, SAND)
    screen.blit(intro_text_line2, (WIDTH // 2 - intro_text_line2.get_width() // 2, HEIGHT // 2 + intro_text_line1.get_height() // 2 + 10))  # 간격 추가

    # "증명하라." 메시지 표시 (세 번째 줄)
    intro_text_line3 = font.render("자격을 증명하라.", True, SAND)
    screen.blit(intro_text_line3, (WIDTH // 2 - intro_text_line3.get_width() // 2, HEIGHT // 2 + intro_text_line1.get_height() // 2 + intro_text_line2.get_height() + 10))  # 간격 추가

    pygame.display.update()
    time.sleep(3)  # 3초 동안 대기

# 게임 루프
def game():
    global heart
    question_index = 0
    
    intro_screen()  # 인트로 화면 표시

    #BGM시작
    pygame.mixer.music.play(-1)
    
    while heart > 0 and question_index < len(questions):
        question, correct_option, wrong_option = questions[question_index]
        
        # 1번과 2번의 선택지를 랜덤으로 배치
        if random.choice([True, False]):
            option1 = correct_option
            option2 = wrong_option
        else:
            option1 = wrong_option
            option2 = correct_option
        
        # 제한시간 설정
        time_limit = 8
        selected_option = None
        
        start_ticks = pygame.time.get_ticks()  # 시작 시간
        while True:
            time_left = time_limit - (pygame.time.get_ticks() - start_ticks) // 1000
            if time_left <= 0:
                break  # 시간이 다 되면 빠져나감
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        selected_option = option1
                    elif event.key == pygame.K_2:
                        selected_option = option2
                    elif event.key == pygame.K_p:
                        pygame.mixer.music.play(-1)
                    elif event.key == pygame.K_s:
                        pygame.mixer.music.stop()
            
            # 문제와 선택지, 시간, 선택한 답안 표시
            display_question(question, option1, option2, time_left, selected_option)
        
        # 정답 여부와 하트 처리
        if selected_option == correct_option:
            # 정답일 경우
            display_question(question, option1, option2, 2, selected_option)
            result_text = big_font.render("통과", True, GREEN)
            screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT // 2))
            pygame.display.update()
            time.sleep(2)  # 2초 대기
        else:
            # 오답일 경우
            display_question(question, option1, option2, 2, selected_option)
            result_text = big_font.render("오답", True, RED)
            screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT // 2))
            pygame.display.update()
            time.sleep(2)  # 2초 대기
            heart -= 1  # 하트 하나 감소
        
        question_index += 1

    # 게임 종료 메시지
    screen.fill(BLACK)
    if heart > 0:
        result_text = big_font.render("통과", True, SAND)
    else:
        result_text = big_font.render("플레이어가 사망하였습니다.", True, RED)
    screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()
    time.sleep(3)  # 3초 대기 후 종료

# 게임 시작
game()

# 파이게임 종료
pygame.quit()
