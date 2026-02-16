    const windowEl = document.getElementById("myWindow");
    const titleBar = document.getElementById("titleBar");

    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");

    const backgroundColor = "#d6d6d6";
    ctx.fillStyle = backgroundColor;
    ctx.fillRect(0, 0, 10000, 10000);

    //call resizeCanvas() if the windo size is changing
    window.addEventListener("resize", resizeCanvas);

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resizeCanvas(); // initial sizing


    function drawAllRunways(numberOfRuns, modes){

        // most imoprtant sittings 
        let size = 130
        const runwayHorizontalGap = Math.round(size * 0.3);
        const runwayVerticalGap = Math.round(size * 1);


    /*  mode = 1 accept arrivals
        mode = -1 accept departure
        mode = 0 accept both */
        function drawRunway(x, y, mode, runSize){

            let runwaySize = runSize;
            const lindeWidth = 4

            // draw big box
            ctx.strokeStyle = "black";
            ctx.lineWidth = lindeWidth;
            ctx.strokeRect(x, y, runwaySize, runwaySize);
            
            // transform the coordinates and runwaySize to the small box above the runway big box
            x += runwaySize/4
            runwaySize /= 2
            y -= runwaySize

            // draw small box
            ctx.strokeRect(x, y, runwaySize, runwaySize);

            // arrows sittings
            const arrowsDistence = runwaySize * 0.4;
            const arrowsLength = runwaySize * 0.7;
            const arrowsPointerLength = arrowsLength * 0.3;
            
            x += runwaySize/2;
            y += runwaySize/2;

            ctx.lineWidth = lindeWidth/2;

            if(mode >= 0){
                // draw red arrow
                ctx.strokeStyle = 'red';
                ctx.beginPath();
                ctx.moveTo(x - arrowsDistence/2, y + arrowsLength/2);//tail
                ctx.lineTo(x - arrowsDistence/2, y - arrowsLength/2);//head 
                ctx.stroke();

                ctx.beginPath();
                ctx.moveTo(x - arrowsDistence/2, y - arrowsLength/2);
                ctx.lineTo(x - arrowsDistence/2 - arrowsPointerLength, y - arrowsLength/2 + arrowsPointerLength);
                ctx.stroke();

                ctx.beginPath();
                ctx.moveTo(x - arrowsDistence/2, y - arrowsLength/2);
                ctx.lineTo(x - arrowsDistence/2 + arrowsPointerLength, y - arrowsLength/2 + arrowsPointerLength);
                ctx.stroke();
            }

            if(mode <= 0){
                // draw blue arrow
                ctx.strokeStyle = 'blue';
                ctx.beginPath();
                ctx.moveTo(x + arrowsDistence/2, y - arrowsLength/2);//tail
                ctx.lineTo(x + arrowsDistence/2, y + arrowsLength/2);//head 
                ctx.stroke();

                ctx.beginPath();
                ctx.moveTo(x + arrowsDistence/2, y + arrowsLength/2);
                ctx.lineTo(x + arrowsDistence/2 - arrowsPointerLength, y + arrowsLength/2 - arrowsPointerLength);
                ctx.stroke();

                ctx.beginPath();
                ctx.moveTo(x + arrowsDistence/2, y + arrowsLength/2);
                ctx.lineTo(x + arrowsDistence/2 + arrowsPointerLength, y + arrowsLength/2 - arrowsPointerLength);
                ctx.stroke();    
            }
        }

        let startX;
        let startY;

        if(numberOfRuns <= 5){
            startY = (canvas.height - size) / 2
            startX = (canvas.width - (numberOfRuns * size + (numberOfRuns - 1) * runwayHorizontalGap)) / 2;
        }
        else{
            startY = (canvas.height - size) / 2 - runwayVerticalGap
            startX = (canvas.width - (5 * size + 4 * runwayHorizontalGap)) / 2;
        }



        
        for(let i=0; i<5 && i<numberOfRuns; i++){
            drawRunway(startX + i*(size+runwayHorizontalGap), startY, 0, size)
        }

        if(numberOfRuns > 5){
            startX = (canvas.width - ((numberOfRuns - 5) * size + (numberOfRuns - 6) * runwayHorizontalGap)) / 2;
            startY += size + runwayVerticalGap;
            for(let i=0; i<5 && i<numberOfRuns-5; i++){
                drawRunway(startX + i*(size+runwayHorizontalGap), startY, 0, size)
            }
        }
    }

    drawAllRunways(5,0);






