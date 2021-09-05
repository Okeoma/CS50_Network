var updated_form = null;
document.addEventListener('DOMContentLoaded', function () {
	
	//Loads the Edit form when edit link is clicked    
    document.querySelectorAll("[id^='edit_link_']").forEach(a => {a.onclick = function () {
            if (updated_form != null) {
                hideForm(updated_form);
            }
            updated_form = this;
			let form = document.querySelector('#form_edit' + this.dataset.id);
            let tweets = document.querySelector('#tweet' + this.dataset.id);            
            tweets.style.display = 'none';
            form.querySelector('#edit_text').value = tweets.innerHTML;
            form.style.display = '';
        };

    });
	
	//Hides the Edit form when triggered by an element     
    function hideForm(element) {
		let form = document.querySelector('#form_edit' + element.dataset.id);
        let tweets = document.querySelector('#tweet' + element.dataset.id);        
        tweets.style.display = '';
        form.querySelector('#edit_text').value = tweets.innerHTML;
        form.style.display = 'none';
    }
	
	//Closing the Edit form when the close button is clicked    
    document.querySelectorAll("[id^='close_btn']").forEach(a => {
        a.onclick = function () {
            hideForm(this);
        };

    });
    
	
    //Allows for the Sending of text via the post form by a submit request	
    document.querySelectorAll("[id^='form_edit']").forEach(form => {
        form.onsubmit = function (e) {
            e.preventDefault();
            this.querySelector('#post_button').style.display = "none";
            if (this.querySelector("#alert_message") != null) {
                this.querySelector("#alert_message").remove();
            }
			//'alert'- Gives a response via an alert on the status of the message via post
            let alert = this.querySelector("#post_alert" + this.dataset.id);

            let input = this.querySelector('div>textarea');
			//Prompts the user to enter text in the post form if empty
            if (input.value.trim().length == 0) {
                alertInfo({
                    "error": "You are required to enter text here"
                }, alert, this.dataset.id);
                this.querySelector('#post_button').style.display = "";
                return 0;
            }
			//Submits post form or issue message if unsuccessful
            var formData = $(this).serialize();
            let csrftoken = this.querySelector("input[name='csrfmiddlewaretoken']").value;
            fetch(`/editpost/${this.dataset.id}`, {
                    method: 'POST',
                    headers: {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        "X-CSRFToken": csrftoken
                    },
                    body: formData
                })
                .then(response => response.json())
                .then(data => {

                    alertInfo(data, alert, this.dataset.id);
                    this.querySelector('#post_button').style.display = "";
                }).catch((error) => {
                    alertInfo({
                        'error': error.message
                    }, alert, this.dataset.id);
                    this.querySelector('#post_button').style.display = "";
                });
        }

    });	
	
	
	//Shows error or success alert message
    function alertInfo(data, alert, id) {
        let div = document.createElement("div");
        let sucess = false;
        div.setAttribute("role", "alert");
        div.setAttribute("id", "alert_message");
        if (document.getElementById('alert_message') == null) {
            if (data.error) {
                if (data.error.edit_text) {
                    div.innerHTML = data.error.edit_text.join();
                } else {
                    div.innerHTML = data.error;
                }
                div.className = "alert alert-dismissible fade alert-danger in show";
            } else {
                sucess = true;
                document.querySelector("#tweet" + id).innerHTML = data.text;
                div.innerHTML = "Post changed successfully!";
                div.className = "alert alert-dismissible fade alert-success in show";
            }
        }
        alert.appendChild(div);
        var alert_message = document.getElementById("alert_message");
        setTimeout(function () {
            if (alert_message != null) {
                $(alert_message).fadeOut("fast");
                alert_message.remove();
                if (sucess) {
                    document.querySelector("#form_edit" + id).style.display = "none";
                    document.querySelector("#tweet" + id).style.display = "";
                }
            }
        }, 1000);
    }
	
		
	//toggling between following and follow options in the profile page
    if (document.getElementById("followering_btn")) {
        document.querySelector("#followering_btn").addEventListener("click", function (event) {
            fetch(`/follow/${this.dataset.id}`)
                .then(response => response.json())
                .then(data => {
                    document.querySelector('#followers').innerHTML = data.total_followers;
                    if (data.sequel == "follow") {
                        this.innerHTML = "Following";
                        this.className = "btn btn-primary";
                    } else {
                        this.innerHTML = "Follow";
                        this.className = "btn btn-outline-primary";
                    }
                });

        })

        //Gives the Unfollow option when the mouse pointer leaves the Following button        
        document.querySelector("#followering_btn").addEventListener("mouseover", function (event) {
            if (this.className == "btn btn-primary") {
                this.innerHTML = "Unfollow"
            }
        });

        //Gives the Following option when the mouse pointer leaves the Following button
        document.querySelector("#followering_btn").addEventListener("mouseleave", function (event) {
            if (this.className == "btn btn-primary") {
                this.innerHTML = "Following"
            }
        });

    }
	
	//Creates likes toggle option for users to select by calling the onclick method	
    document.querySelectorAll(".fa-heart").forEach(div => {
        div.onclick = function () {
            likesToggle(this);
        };
    });
	
	//Calls the like method when triggered by an element    
    async function likesToggle(element) {
        await fetch(`/like/${element.dataset.id}`)
            .then(response => response.json())
            .then(data => {
                element.className = data.like_class;
                element.querySelector("small").innerHTML = data.total_likes;
            });
    }
		
    
});

$(document).on('submit', '#deletePost', function(e){
    e.preventDefault();
    postId = $(this).data('post')
    post = $(`#post${postId}`)

    $.ajax({
        type:'POST',
        url: $(this).attr('action'),
        data: $(this).serialize(),
        success: function() {
            console.log('deleted')
            comment.remove()
        }
    })

})