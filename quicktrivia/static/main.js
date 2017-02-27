"use strict"

var STATES = {
  READY     : "Ready to submit answer",
  SUBMITTED : "Answer has been submitted"
};

var currState;
var answerTimeout;

$(document).ready(function(){
  currState = STATES.READY

  $('.main-container').on('click', '.begin-btn', function(event) {
    getNextQuestion();
  });

  $('body').on('click', '.answer', function(event){
    if (currState === STATES.READY) {
      currState = STATES.SUBMITTED;
      var question_id = $('.question').attr('id').split('-')[1];
      var $answer = $(this);
      var answer_id = $answer.attr('id').split('-')[1];
      $.post('/',
             { q_id : question_id, answer_id: answer_id },
             function(data){
               var prevStreak = $('#streak').html();
               var correct_id = data['correct_answer'];
               $answer.addClass('wrong');
               $('#answer-' + correct_id).addClass('correct');

               if (parseInt(answer_id) === correct_id) {
                 $('#streak').html(data['streak']);
                 setTimer($('#timer'), 2);
                 setTimeout(getNextQuestion, 2000);
               }
               else {
                 setTimer($('#timer'), 2);
                 setTimeout(function(){
                   $('.container').html('\
                   You answered correctly ' + prevStreak + ' questions in a row\
                   <div class="begin-btn">Try Again</div>\
                  ');
                  currState = STATES.READY;
                }, 2000);
               }
             }
             );
      } // currState === READY
    });
});

var getNextQuestion = function() {
  currState = STATES.READY;
  $.get('/', function(data) {
    $('.main-container').append(data);
    var $first = $('.full-width-container').first();
    $first.animate({ 'margin-left' : '-50%' }).promise().done(function(){
      $first.remove();
    });
  });

}

var setTimer = function($timer, duration) {
  $timer.css({ 'visibility': 'visible' });
  $timer.html(duration);
  var interval = setInterval(function(){
    var time_left = parseInt($timer.html());
    if (time_left === 1) {
      clearInterval(interval);
    }
    $timer.html(time_left - 1)
  }, 1000);
}
