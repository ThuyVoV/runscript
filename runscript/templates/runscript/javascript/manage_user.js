let select_user = document.getElementById("select_user") //dropdown list of user
let user = document.getElementById("btn_select_user") // select user button
let show_perm = document.getElementById("show_perm")
let btn_change_perm = document.getElementById("btn_change_perm")
let btn_del_user = document.getElementById("btn_del_user")

console.log("doing whatever")
// console.log("ajax", su.value)
// console.log("btn", user)
// console.log("this is hehe", hehe)
//user.children("option").filter(":selected").text()

// user.addEventListener("click", e => {
//     e.preventDefault()
//     ajaxtest.classList.remove("novis")
//
// })


user.addEventListener("click", e => {
    e.preventDefault()

    $.ajax({
        type: 'GET',
        url: "",
        data: {
            "selected_user": select_user.value,
            "pressed": "select"
        },
        success: function (response) {
            console.log('success', response)
            console.log('check perm', response.check_perm)
            console.log('perm atr', response.perm_attributes)

            perm = response.check_perm
            attr = response.perm_attributes
            // user.addEventListener("click", e => {
            su = document.getElementById("select_user")
            console.log("select_user.value",select_user.value)

            show_perm.classList.remove("novis")
            btn_change_perm.classList.remove("novis")
            btn_del_user.classList.remove("novis")
            console.log("clicked bbutton")

            show_perm.innerHTML = `<div>Editing Permissions for user: ${select_user.value}</div>`

            for (let i = 0; i < response.check_perm.length; i++) {
                if (perm[i]) {
                    show_perm.innerHTML +=
                    `<div>
                    <input class="form-check-inline" type="checkbox" name="perm_checkbox" value="clicked" checked> ${attr[i]}
                    </div>`
                } else {
                    show_perm.innerHTML +=
                    `<div>
                    <input class="form-check-inline" type="checkbox" name="perm_checkbox" value="clicked"> ${attr[i]}
                    </div>`
                }
            }
            // })

        },
        error: function (error) {
            console.log('error', error)
        }
    })
})

btn_change_perm.addEventListener("click", e =>{
    console.log("clicked change perm")

    let p_list = document.getElementsByName("perm_checkbox")
    let perm_list = []
    console.log("p_list", p_list)
    for ( let i = 0; i < p_list.length ; i++){
        console.log(p_list[i].checked)
        perm_list.push(p_list[i].checked)
    }

    console.log("perm_list",perm_list)

    $.ajax({
        type: 'POST',
        url: "",
        data: {
            "selected_user": select_user.value,
            "pressed": "perm",
            "csrfmiddlewaretoken": csrftoken,
            "perm_list": perm_list
        },
        success: function (response) {
            console.log("success")
            console.log("this is the messages", response.message)
            let msg_div = document.getElementById("perm_msg")

            msg_div.innerHTML = ``
            response.message.forEach ( x =>
                msg_div.innerHTML += `<div>${x}</div>`
            )
            show_perm.classList.add("novis")
            btn_change_perm.classList.add("novis")
            btn_del_user.classList.add("novis")
        },
        error: function (error) {
            console.log('error', error)
        }
    })
})

btn_del_user.addEventListener("click", e =>{
    console.log("clicked del user")
    $.ajax({
        type: 'POST',
        url: "",
        data: {
            "selected_user": select_user.value,
            "pressed": "delete",
            'csrfmiddlewaretoken': csrftoken,
        },
        success: function (response) {
            console.log("success")

        },
        error: function (error) {
            console.log('error', error)
        }
    })
})

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// $.ajax({
//     type: 'GET',
//     url: "",
//     data: {
//         "selected_user": su.value,
//     },
//     success: function (response) {
//         console.log('success', response)
//         console.log("script_list", response.script_list)
//         console.log('check perm', response.check_perm)
//         console.log('perm atr', response.perm_attributes)
//
//         // const data = response.perm_attributes
//         console.log(response.check_perm.length)
//         console.log(response.perm_attributes.length)
//         perm = response.check_perm
//         attr = response.perm_attributes
//         user.addEventListener("click", e => {
//             su = document.getElementById("select_user")
//             console.log(su.value)
//             e.preventDefault()
//             ajaxtest.classList.remove("novis")
//             console.log("clicked bbutton")
//
//             ajaxtest.innerText = ``
//
//             for (let i = 0; i < response.check_perm.length; i++) {
//                 if (perm[i]) {
//                     ajaxtest.innerHTML +=
//                         `<label>
//                     <input class="form-check-inline" type="checkbox" name="${attr[i]}" value="clicked" checked> ${attr[i]}
//                     </label>`
//                 } else {
//                     ajaxtest.innerHTML +=
//                         `<label>
//                     <input class="form-check-inline" type="checkbox" name="${attr[i]}" value="clicked" >${attr[i]}
//                     </label>`
//                 }
//             }
//         })
//
//     },
//     error: function (error) {
//         console.log('error', error)
//     }
// })