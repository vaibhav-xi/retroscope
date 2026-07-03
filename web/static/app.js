//
// RetroScope Web UI
//

async function getState() {

    const response = await fetch("/api/state");

    const state = await response.json();

    //
    // Waveform
    //

    document.querySelector(
        `input[name="wave"][value="${state.waveform}"]`
    ).checked = true;

    //
    // Sliders
    //

    frequency.value = state.frequency;
    amplitude.value = state.amplitude;

    freqValue.innerText =
        Number(state.frequency).toFixed(2) + " Hz";

    ampValue.innerText =
        Number(state.amplitude).toFixed(2);

    //
    // Checkboxes
    //

    glow.checked = state.glow;
    grid.checked = state.grid;
    scanlines.checked = state.scanlines;
    persistence.checked = state.persistence;
    noise.checked = state.noise;
}


//--------------------------------------------------------

async function update(values){

    await fetch("/api/update",{

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify(values)

    });

}

//--------------------------------------------------------
// Waveforms
//--------------------------------------------------------

document
.querySelectorAll('input[name="wave"]')
.forEach(control=>{

    control.onchange=()=>{

        update({

            waveform:control.value

        });

    };

});

//--------------------------------------------------------
// Frequency
//--------------------------------------------------------

frequency.oninput=()=>{

    freqValue.innerText=
        Number(frequency.value).toFixed(2)+" Hz";

    update({

        frequency:Number(frequency.value)

    });

};

//--------------------------------------------------------
// Amplitude
//--------------------------------------------------------

amplitude.oninput=()=>{

    ampValue.innerText=
        Number(amplitude.value).toFixed(2);

    update({

        amplitude:Number(amplitude.value)

    });

};

//--------------------------------------------------------
// Effects
//--------------------------------------------------------

glow.onchange=()=>{

    update({

        glow:glow.checked

    });

};

grid.onchange=()=>{

    update({

        grid:grid.checked

    });

};

scanlines.onchange=()=>{

    update({

        scanlines:scanlines.checked

    });

};

noise.onchange=()=>{

    update({

        noise:noise.checked

    });

};

persistence.onchange=()=>{

    update({

        persistence:persistence.checked

    });

};

//--------------------------------------------------------
// Reset
//--------------------------------------------------------

reset.onclick=async()=>{

    await fetch("/api/reset",{

        method:"POST"

    });

    getState();

};

//--------------------------------------------------------

getState();
