let su = document.getElementById("select_user")
let user = document.getElementById("btn_select_user")
let ajaxtest = document.getElementById("ajaxtest")
// let hehe = document.getElementsByTagName("form")[0].getAttribute("action")

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

$.ajax({
    type: 'GET',
    url: "",
    data: {
        "selected_user": su.value,
    },
    success: function (response) {
        console.log('success', response.can_view)
        console.log("script_list", response.script_list)
        console.log('check perm', response.check_perm)
        console.log('perm atr', response.perm_attributes[0])
        console.log('perm atr', response.perm_attributes[2])
        const data = response.perm_attributes

        user.addEventListener("click", e => {
            e.preventDefault()
            ajaxtest.classList.remove("novis")
            console.log("clicked bbutton")
            data.forEach( el =>{
                // ajaxtest.innerHTML += `
                //     ${el}
                // `

            })

        })

    },
    error: function (error) {
        console.log('error', error)
    }
})
