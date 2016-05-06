function upload(event) {
    event.preventDefault();
    var data = new FormData($('#upload_form').get(0));
    $('#upload_form').children().prop('disabled', true);

    $.ajax({
        url: $(this).attr('action'),
        type: $(this).attr('method'),
        data: data,
        cache: false,
        processData: false,
        contentType: false,
        success: function(data) {
            $('#upload_form').children().prop('disabled', false);
            $("#video_name").html(data);
            $("#current_frame").html(0);
            select_video();
        }
    });
    return false;
}

$(function() {
    $('#upload_form').submit(upload);
});


function select_video(){
    $.ajax({
        url: '/main/select_video/',
        data: {video_name:$("#video_name").html()},
        contentType: "application/json",
    }).done(function(data) {
        $('#pointer_div').attr('style', 'background-image:url("/static/main_app/media/' +data+'");border:1px solid black');
        alert('ok');
    });
}

function get_train_frame(event){
    event.preventDefault();
    $.ajax({
        url: '/main/get_train_frame/',
        data: {video_name:$("#video_name").html(), current_frame:$("#current_frame").html()},
        contentType: "application/json",
    }).done(function(data) {
        $("#current_frame").html(parseInt($("#current_frame").html()) + 100);
        $('#pointer_div').attr('style', 'background-image:url("/static/main_app/media/' +data+'");border:1px solid black');
    });
}

function detect_cmd(event){
    var json_data = {}
    json_data["data"] = sessionStorage.getItem('lane');
    json_data["video_name"] = $("#video_name").html();
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
