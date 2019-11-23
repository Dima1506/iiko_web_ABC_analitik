  var cost_1 = 0;
  var cost_2 = 0;
  var cost_4 = cost_1 + cost_2;
  var cost_3 = cost_4*0.7;
  document.getElementById("cost2").innerHTML = cost_1.toFixed(2);
  document.getElementById("cost3").innerHTML = cost_2.toFixed(2);
  document.getElementById("cost1").innerHTML = cost_3.toFixed(2);
  document.getElementById("cost4").innerHTML = cost_4.toFixed(2);
  function f(){
    cost_1=document.getElementById('sel1').options.selectedIndex;
    var array = JSON.parse("[" + cost1 + "]");
    cost_1 = array[0][cost_1-1]
    cost_4 = cost_1 + cost_2;
    cost_3 = cost_4*0.7;
    document.getElementById("cost2").innerHTML = cost_1.toFixed(2);
    document.getElementById("cost1").innerHTML = cost_4.toFixed(2);
    document.getElementById("cost4").innerHTML = cost_3.toFixed(2);
  }
  function f2(){
    cost_2=document.getElementById('sel1').options.selectedIndex;
    var array = JSON.parse("[" + cost2 + "]");
    cost_2 = array[0][cost_2-1]
    cost_4 = cost_1 + cost_2;
    cost_3 = cost_4*0.7;
    document.getElementById("cost1").innerHTML = cost_4.toFixed(2);
    document.getElementById("cost3").innerHTML = cost_2.toFixed(2);
    document.getElementById("cost4").innerHTML = cost_3.toFixed(2);
  }
 
  var csrf_token = '{{ csrf_token }}';
  var state = '{{state}}'
  var cpa = '{{CPA}}'
  var arc = '{{ARC}}'
  var arpu_cpa_arc = '{{ARPU_CPA_ARC}}'
  var revenue = '{{Revenue}}'
  var roi = '{{ROI}}'
  var cost1 = '{{cost1}}'
  var cost2 = '{{cost2}}'