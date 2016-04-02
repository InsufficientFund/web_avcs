function send_predict(event){

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

var app = angular.module("MainApp", ['n3-pie-chart', 'ngProgress']);
app.config(function($interpolateProvider){
$interpolateProvider.startSymbol('{-').endSymbol('-}');
});
app.controller('MainController', ['$scope', '$http', '$interval', 'ngProgressFactory' ,function($scope,$http,$interval, ngProgressFactory) {
    $scope.title = 'Top Sellers in Books';
    $scope.test_api_call = function(){
        $http({method:'GET', url:'test_api/'})
            .then(function(response){
                debugger;
            });
            debugger;
        };
    $scope.progressbar = ngProgressFactory.createInstance();
    $scope.progressbar.setHeight('10px');
    //ngProgress.set(100);
    // $http({method:'GET', url:'get_graph_data/'})
    // .then(function(response){
    //     angular.forEach(response['data'],function(type_data){
    //       var a = [];
    //       a.push({type_data})
    //     })
    // });
    $scope.data = [
        {label: "Bikes", value: 0, color: "red"},
        {label: "Passenger cars", value: 0, color: "#00ff00"},
        {label: "Truck", value: 0, color: "rgb(0, 0, 255)"}
    ];
    $scope.options = {thickness: 10};
    stop = $interval(function() {
        // $http({method:'GET', url:'test_api/'})
        // .then(function(response){
        //   $scope.data = [
        //     {label: "one", value: 12.2, color: "red"},
        //     {label: "two", value: 45, color: "#00ff00"},
        //     {label: "three", value: 10, color: "rgb(0, 0, 255)"}
        //   ];
        // });
        $scope.vid_name = $('#video_name').html()
        if($scope.vid_name != "" ){
            $http({method:'GET', url:'get_graph_data/', params:{'video_name':$scope.vid_name}})
            .then(function(response){
                $scope.data = [
                    {label: "Bikes", value: response['data']['s'], color: "red"},
                    {label: "Passenger cars", value: response['data']['m'], color: "#00ff00"},
                    {label: "Trucks", value: response['data']['l'], color: "rgb(0, 0, 255)"}
                ];
                if(($scope.data[0]['value']+$scope.data[1]['value']+$scope.data[2]['value']) > 0){
                    $scope.has_graph_data = true;
                }
                else {
                    $scope.has_graph_data = false;
                }
            });
            $http({method:'GET', url:'get_progress_data/', params:{'video_name':$scope.vid_name}})
            .then(function(response){
                current_frame = response['data']['progress'];
                max_frame = response['data']['max_frame'];
                progress = (current_frame * 100)/max_frame;
                if (max_frame != 0){
                    if (current_frame == max_frame){
                        $interval.cancel(stop);
                    }
                    else{
                        $scope.progressbar.set(progress);
                    }
                }

            });
        }
    }, 5000);
    // $scope.has_graph_data = $scope.data[0]['value']+$scope.data[1]['value']+$scope.data[2]['value']
    // if(($scope.data[0]['value']+$scope.data[1]['value']+$scope.data[2]['value']) > 0){
    //   $scope.has_graph_data = true;
    // }
    // else {
    //   $scope.has_graph_data = false;
    // }
}]);