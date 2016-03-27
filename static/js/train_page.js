function select_video(){
    $.ajax({
        url: '/main/select_video/',
        data: {video_name:$("#video_name").val()},
        contentType: "application/json",
    }).done(function(data) {
        $('#pointer_div').attr('style', 'background-image:url("/static/main_app/media/' +data+'");border:1px solid black');
        alert('ok');
    });
}

function detect_cmd(event){
    var json_data = {}
    json_data["data"] = sessionStorage.getItem('lane');
    json_data["video_name"] = $("#video_name").val();
    $.ajax({
        url: "/main/detect/",
        type: "POST",
        data: JSON.stringify(json_data),//JSON.stringify(sessionStorage.getItem('lane')),
        contentType: "application/json",
        success:function(data) {
            $("#cars_image").html(data);
        },
    });
}

function send_select(event){
    console.log('send');
    var formData = $("#select_form").serializeArray();
    $.post('/main/imp_data/', JSON.stringify(formData)).done(function (data) {
        $("#cars_image").html('');
        alert(data);
    });
}

function train_cmd(event){
    console.log('train');
    $.ajax({
      url: '/main/train/'
    }).done(function(data) {
      alert(data);
    });
}