import matplotlib.pyplot as plt

def draw_dependency_structure():
    # מיקומים (x, y) של כל "צומת" (מילה/צירוף)
    positions = {
        "ברא": (0, 2),                 # הפועל (שורש)
        "ב ראשית": (-1.5, 0),          # צירוף הזמן
        "אלהים": (0, 0),               # הנושא
        "את השמים ו את הארץ": (1.5, 0) # המושא
    }

    # רישום הטקסט (צמתים) על התרשים
    for token, (x, y) in positions.items():
        plt.text(x, y, token, ha='center', va='center', fontsize=12)

    # ציור חיצים (תלות) מהשורש ("ברא") אל שאר המרכיבים
    # annotate: מאפשר להוסיף חץ ותווית
    # xy  -> נקודת הילד
    # xytext -> נקודת האב
    # arrowprops -> סגנון החץ (אין הגדרת צבע ספציפית)

    def draw_arrow(parent, child, label):
        px, py = positions[parent]
        cx, cy = positions[child]
        plt.annotate(
            label,
            xy=(cx, cy),
            xytext=(px, py),
            arrowprops={"arrowstyle": "->"},
            ha='center'
        )

    # חצים (תלות תחבירית):
    draw_arrow("ברא", "ב ראשית", "Time")  # צירוף זמן
    draw_arrow("ברא", "אלהים", "Subj")    # נושא
    draw_arrow("ברא", "את השמים ו את הארץ", "Obj")  # מושא ישיר

    # התאמות תצוגה: הסרת צירים, התאמת גבולות
    plt.axis('off')
    plt.xlim(-3, 3)
    plt.ylim(-1, 3)

    plt.title("Dependency structure (ברא אלהים ב ראשית את השמים ואת הארץ)")
    plt.show()

if __name__ == "__main__":
    draw_dependency_structure()
