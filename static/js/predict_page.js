function select_video(){
    console.log('video');
    $.ajax({
        url: '/main/get_sample_frame/',
        data: {video_name:$("#video_name").html()},
        contentType: "application/json",
    }).done(function(data) {
        $('#pointer_div').attr('style', 'background-image:url("/static/main_app/media/' +data+'");border:1px solid black');
    });
}

function get_predict_frame(event){
    event.preventDefault();
    $.ajax({
        url: '/main/get_predict_frame/',
        data: {video_name:$("#video_name").html(), current_frame:$("#sample_frame").html()},
        contentType: "application/json",
    }).done(function(data) {
        $("#sample_frame").html(parseInt($("#sample_frame").html()) + 100);
        $('#pointer_div').attr('style', 'background-image:url("/static/main_app/media/' +data+'");border:1px solid black');
    });
}

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
            $("#sample_frame").html(0);
            select_video();
        }
    });
    return false;
}

$(function() {
    $('#upload_form').submit(upload);
});

var app = angular.module("MainApp", ['n3-pie-chart', 'ngProgress', 'n3-line-chart']);
app.config(function($interpolateProvider){
    $interpolateProvider.startSymbol('{-').endSymbol('-}');
});
app.controller('MainController', ['$scope', '$http', '$interval', 'ngProgressFactory' ,function($scope,$http,$interval, ngProgressFactory) {
    $scope.title = 'Top Sellers in Books';
    $scope.is_submitted = false;
    $scope.progressbar = ngProgressFactory.createInstance();
    $scope.progressbar.setHeight('10px');
    $scope.data = [
        {label: "Bikes", value: 0, color: "red"},
        {label: "Passenger cars", value: 0, color: "#00ff00"},
        {label: "Truck", value: 0, color: "rgb(0, 0, 255)"}
    ];
    $scope.is_predicting = false;
    $scope.data_line = {
        dataset0: [
          {x: 0, s_car: 0, m_car: 0, l_car: 0},
          {x: 1, s_car: 0, m_car: 0, l_car: 0},
          {x: 2, s_car: 0, m_car: 0, l_car: 0},
          {x: 3, s_car: 0, m_car: 0, l_car: 0},
          {x: 4, s_car: 0, m_car: 0, l_car: 0},
          {x: 5, s_car: 0, m_car: 0, l_car: 0},
          {x: 6, s_car: 0, m_car: 0, l_car: 0},
          {x: 7, s_car: 0, m_car: 0, l_car: 0},
          {x: 8, s_car: 0, m_car: 0, l_car: 0},
          {x: 9, s_car: 0, m_car: 0, l_car: 0},
          {x: 10, s_car: 0, m_car: 0, l_car: 0},
        ]
    };

    $scope.options_line = {
      series: [
        {
          axis: "y",
          dataset: "dataset0",
          key: "s_car",
          label: "Bikes",
          color: "rgb(255, 0, 0)",
          type: ['line', 'dot'],
          id: 'mySeries0'
        },
        {
          axis: "y",
          dataset: "dataset0",
          key: "m_car",
          label: "Passenger cars",
          color: "rgb(0, 255, 0)",
          type: ['line', 'dot'],
          id: 'mySeries1'
        },
        {
          axis: "y",
          dataset: "dataset0",
          key: "l_car",
          label: "Truck",
          color: "rgb(0, 0, 255)",
          type: ['line', 'dot'],
          id: 'mySeries2'
        }
      ],
      axes: {x: {key: "x"}},
      margin: {
        top: 20
      }
    };
    $scope.options = {thickness: 10};
    $scope.max_frame = 0 ;
    $scope.send_predict = function($event){
        $scope.progressbar.set(0);
        var json_data = {}
        json_data["data"] = sessionStorage.getItem('lane');
        json_data["video_name"] = $("#video_name").html();
        json_data["email"] = $("#email").val();
        $scope.is_predicting = true;
        $.ajax({
            url: "/main/predict/",
            type: "POST",
            data: JSON.stringify(json_data),
            contentType: "application/json",
            success:function(data) {

            },
        });

      a = $interval(function(){
        console.log($scope.is_submitted);
      },1000);
      stop = $interval(function() {
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
                  $scope.max_frame = response['data']['max_frame'];
                  progress = (current_frame * 100)/$scope.max_frame;
                  if ($scope.max_frame != 0){
                      if (current_frame == $scope.max_frame){
                          $scope.progressbar.set(100);
                          $interval.cancel(stop);
                      }
                      else{
                          $scope.progressbar.set(progress);
                      }
                  }

              });
              if($scope.max_frame>0){
                $http({method:'GET', url:'get_line_data/', params:{'video_name':$scope.vid_name, 'max_frame':$scope.max_frame}})
                .then(function(response){
                    for(var i=0; i<10; i++){
                        $scope.data_line['dataset0'][i+1]['s_car'] = response['data'][i]['s']
                        $scope.data_line['dataset0'][i+1]['m_car'] = response['data'][i]['m']
                        $scope.data_line['dataset0'][i+1]['l_car'] = response['data'][i]['l']
                    }
                });
              }
                $.ajax({
                    url: '/main/result_image/',
                    data: {video_name:$("#video_name").html()},
                    contentType: "application/json",
                }).done(function(data) {
                    $('#result').html(data);
                });
            }
        }, 5000);
      }

}]);
