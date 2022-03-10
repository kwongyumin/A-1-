
        function delete_post(){
            $.ajax({
                    type: "POST",
                    url: `/delete_post`,
                    data: {
                        num_give: "{{ num }}"
                    },
                    success: function (response) {
                        alert(response["msg"])
                        window.location.href = "/"
                    }
                });
        }

        function update_post(num){





            window.location.href = "/update_post/"+num
        }

        function toggle_like(num){
            console.log(num)
            let $a_like = $(`a[aria-label='heart']`)
            let $i_like = $a_like.find("i")


            if($i_like.hasClass("fa-solid")){
                $.ajax({
                    type: "POST",
                    url: "/update_like",
                    data: {
                        num_give: num,
                        action_give: "unlike"
                    },
                    success: function (response) {
                        console.log("unlike")
                        $i_like.addClass('fa-regular').removeClass('fa-solid')
                        $a_like.find("span.like-num").text(response["count"])
                    }
                })
            }else{
                 $.ajax({
                    type: "POST",
                    url: "/update_like",
                    data: {
                        num_give: num,
                        action_give: "like"
                    },
                    success: function (response) {
                        console.log("like")
                        $i_like.addClass("fa-solid").removeClass("fa-regular")
                        $a_like.find("span.like-num").text(response["count"])
                    }
                })
            }
        }
