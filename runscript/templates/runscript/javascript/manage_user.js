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

user.addEventListener("click", e => {
    e.preventDefault()

    $.ajax({
        type: 'GET',
        url: "",
        data: {
            "selected_user": su.value,
        },
        success: function (response) {
            console.log('success', response)
            console.log("script_list", response.script_list)
            console.log('check perm', response.check_perm)
            console.log('perm atr', response.perm_attributes)

            perm = response.check_perm
            attr = response.perm_attributes
            // user.addEventListener("click", e => {
            su = document.getElementById("select_user")
            console.log("su.value",su.value)

            ajaxtest.classList.remove("novis")
            console.log("clicked bbutton")

            ajaxtest.innerText = ``

            for (let i = 0; i < response.check_perm.length; i++) {
                if (perm[i]) {
                    ajaxtest.innerHTML +=
                        `<label>
                    <input class="form-check-inline" type="checkbox" name="${attr[i]}" value="clicked" checked> ${attr[i]}
                    </label>`
                } else {
                    ajaxtest.innerHTML +=
                        `<label>
                    <input class="form-check-inline" type="checkbox" name="${attr[i]}" value="clicked" >${attr[i]}
                    </label>`
                }
            }
            // })

        },
        error: function (error) {
            console.log('error', error)
        }
    })
})