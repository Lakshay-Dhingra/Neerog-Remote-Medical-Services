$(document).ready(function(){
        $("#countries").on("change",function(){
        var country=$("#countries").val();
        if(country=="Select")
             alert("Select Appropriate Country");
        $.ajax(
        {
             type:"get",
             url:"/Doctor/states/",
             data:
             {
              country:$("#countries").val()
             },
             success:function(data)
             {
             var states=JSON.stringify(data);
             var p=states.split(",");

             $("#states").empty();
             $("#states").append(`<option value="Select">
                                       Select State
                                  </option>`);

             for(var i=0;i<p.length;i++)
             {
             var optionText=p[i].replace("\"","");
                $("#states").append(`<option value="${optionText}">
                                       ${optionText}
                                  </option>`);
             }
             }
        });
        });
        $("#states").on("change",function(){
        var state=$("#states").val();
         if(state=="Select")
             alert("Select Appropriate State");
        $.ajax(
        {
             type:"get",
             url:"/Doctor/city/",
             data:
             {
              city:$("#states").val()
             },
             success:function(data)
             {
             var states=JSON.stringify(data);
             var p=states.split(",");

             $("#cities").empty();
             $("#cities").append(`<option value="Select">
                                       Select City
                                  </option>`);

             for(var i=0;i<p.length;i++)
             {
             var k=p[i].replace("\[","")
             var n=k.replace("\]","")
             var optionText=n.slice(1,n.length-1)

                $("#cities").append(`<option value="${optionText}">
                                       ${optionText}
                                  </option>`);
             }
             }
        });
        });
        $("#form1").on("submit",function()
        {
         var state=$("#states").val();
         var city=$("#cities").val();
         var country=$("#countries").val();
         if(state=="Select" || city=="Select" || country=="Select")
             alert("Select Appropriate values from dropdowns");
        });
        });
