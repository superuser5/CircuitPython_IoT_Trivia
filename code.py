import gc
import displayio
import digitalio
import board
import time
from call_wifi import call_wifi
from fetch_question import fetch_question
from display_text import display_text
from display_answers import display_answers
from wrap_nicely import wrap_nicely
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label


# Config
CUR_QUESTION_OBJ = None
STATE_QUESTION = 0
STATE_ANSWER = 1
STATE_RESULT = 2
CUR_STATE = STATE_QUESTION
current_selected_answer = 0
all_answers = []
score = 0
font = bitmap_font.load_font('SourceSansPro-Regular.bdf')
LINES_VISIBLE = 3
_cur_scroll_index = 0
output_label = label.Label(font, color=0xFFFFFF, max_glyphs=30 * 4)

# Attempt to connect on boot
call_wifi()

# Read trivia.json - if you wanted to try do build a db locally 
# here is an example for you
#f = open('trivia.json', 'r')
#question_str = f.read()
#f.close()
#question_data = json.loads(question_str)
#display_text('\n'.join(wrap_nicely(CUR_QUESTION_OBJ['results'][0]['question'], 25)))

# Pins
c_pin = digitalio.DigitalInOut(board.IO33)
c_pin.direction = digitalio.Direction.INPUT
c_pin.pull = digitalio.Pull.UP
b_pin = digitalio.DigitalInOut(board.IO38)
b_pin.direction = digitalio.Direction.INPUT
b_pin.pull = digitalio.Pull.UP
a_pin = digitalio.DigitalInOut(board.IO1)
a_pin.direction = digitalio.Direction.INPUT
a_pin.pull = digitalio.Pull.UP
old_c_val = c_pin.value
old_b_val = b_pin.value
old_a_val = a_pin.value

while True:
    try:
        if CUR_QUESTION_OBJ is None:
            CUR_QUESTION_OBJ = fetch_question()
            display_text('\n'.join(wrap_nicely(CUR_QUESTION_OBJ['results'][0]['question'], 25)))

        cur_c_val = c_pin.value
        if not cur_c_val and old_c_val:
            print('pressed c')
            if CUR_STATE == STATE_QUESTION:
                CUR_STATE = STATE_ANSWER
                all_answers = CUR_QUESTION_OBJ['results'][0]['incorrect_answers']
                all_answers.append(CUR_QUESTION_OBJ['results'][0]['correct_answer'])
                display_answers(all_answers, current_selected_answer)
            elif CUR_STATE == STATE_ANSWER:
                CUR_STATE = STATE_RESULT
                if all_answers[current_selected_answer] == CUR_QUESTION_OBJ['results'][0]['correct_answer']:
                    score += 1
                    display_text('Correct! YaY\nScore: {}'.format(score))
                else:
                    display_text('Incorrect')
            elif CUR_STATE == STATE_RESULT:
                CUR_STATE = STATE_QUESTION
                CUR_QUESTION_OBJ = None  # clear the question obj to fetch a new one
        old_c_val = cur_c_val

        cur_b_val = b_pin.value
        if not cur_b_val and old_b_val:
            print('pressed b')
        old_b_val = cur_b_val

        cur_a_val = a_pin.value
        if not cur_a_val and old_a_val:
            print('pressed a')
            if CUR_STATE == STATE_QUESTION:
                print(_cur_scroll_index)
                _cur_scroll_index += 1
                print(_cur_scroll_index)
                lines = output_label.text.split("\n")
                if _cur_scroll_index + LINES_VISIBLE > len(lines):
                    _cur_scroll_index = 0
                display_text("\n".join(wrap_nicely(CUR_QUESTION_OBJ['results'][0]['question'], 25)[_cur_scroll_index:]))
            if CUR_STATE == STATE_ANSWER:
                current_selected_answer += 1
                if current_selected_answer > 3:
                    current_selected_answer = 0
                display_answers(all_answers, current_selected_answer)
        old_a_val = cur_a_val

        time.sleep(0.05)
    except Exception as e:
        print(e)
        call_wifi()
