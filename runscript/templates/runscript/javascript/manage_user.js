let su = document.getElementById("select_user")
let user = document.getElementById("btn_select_user")
let ajaxtest = document.getElementById("ajaxtest")
let hehe = document.getElementsByTagName("form")[0].getAttribute("action")

console.log("doing whatever")
// console.log("ajax", su.value)
// console.log("btn", user)
console.log("this is hehe", hehe)
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
        console.log("script_list", response.script_list.user)
        // const data = response.data
        user.addEventListener("click", e => {
            e.preventDefault()
            ajaxtest.classList.remove("novis")

            // data.forEach( el =>{
            //     ajaxtest.innerHTML += `
            //         <option value="Select User">${el}</option>
            //     `
            //     console.log(el)
            // })

        })

    },
    error: function (error) {
        console.log('error', error)
    }
})
