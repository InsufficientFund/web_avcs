function send_predict(event){
    var app = angular.module('progressApp', ['ngProgress']);
    var MainCtrl = function($scope, ngProgressFactory) {
        $scope.progressbar = ngProgressFactory.createInstance();
        $scope.progressbar.start();
        ngProgress.set(100);

    }
    app.controller('progressctrl', MainCtrl);
    var json_data = {}
    json_data["data"] = sessionStorage.getItem('lane');
    json_data["video_name"] = $("#video_name").html();
    json_data["email"] = $("#email").val();
    $.ajax({
        url: "/main/predict/",
        type: "POST",
        data: JSON.stringify(json_data),
        contentType: "application/json",
        success:function(data) {
            alert(data);
        },
    });


}

function select_video(){
    console.log('video');
    $.ajax({
        url: '/main/get_sample_frame/',
        data: {video_name:$("#video_name").html()},
        contentType: "application/json",
    }).done(function(data) {
        $('#pointer_div').attr('style', 'background-image:url("/static/main_app/media/' +data+'");border:1px solid black');
        alert('ok');
    });
}

function upload(event) {
    event.preventDefault();
    var data = new FormData($('#upload_form').get(0));

    $.ajax({
        url: $(this).attr('action'),
        type: $(this).attr('method'),
        data: data,
        cache: false,
        processData: false,
        contentType: false,
        success: function(data) {
            $("#video_name").html(data);
            select_video();
            alert('success');
        }
    });
    return false;
}

$(function() {
    $('#upload_form').submit(upload);
});
