$("#textbox").on("keydown", function (e) {
        if (e.keyCode === 9) {
        e.preventDefault();
        let start = this.selectionStart;
        let end = this.selectionEnd;

        // set textarea value to: text before caret + tab + text after caret
        this.value = this.value.substring(0, start) + "\t" + this.value.substring(end);

        // put caret at right position again
        // if these two dont match it will highlight stuff within the index
        this.selectionStart = this.selectionEnd = start + 1;
        }
    })