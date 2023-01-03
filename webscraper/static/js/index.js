var app = new Vue({
    el: '#app',
    data: {
        message: 'hahahahahah',
    },
    computed: {
        classObject: function () {
            return true
        }
    },
    mounted() {
        this.init(); // -> initialising the vue
    },

    methods: {
        init: function (event) {
            $("#car-icon").click(function () {
            	let element = document.getElementById('id_type');
            	element.value = 'Car';

                document.getElementById('car-icon').classList.add("is-active");
                document.getElementById('motorcycle-icon').classList.remove("is-active");
                document.getElementById('truck-icon').classList.remove("is-active");

            });
            $("#motorcycle-icon").click(function () {
            	let element = document.getElementById('id_type');
            	element.value = 'Motorbike';

                document.getElementById('motorcycle-icon').classList.add("is-active");
                document.getElementById('car-icon').classList.remove("is-active");
                document.getElementById('truck-icon').classList.remove("is-active");
            });
            $("#truck-icon").click(function () {
            	let element = document.getElementById('id_type');
            	element.value = 'Truck';
                document.getElementById('truck-icon').classList.add("is-active");
                document.getElementById('motorcycle-icon').classList.remove("is-active");
                document.getElementById('car-icon').classList.remove("is-active");

            });
            $("#id_type").change(function (event) {
            	document.getElementById('truck-icon').classList.remove("is-active");
                document.getElementById('motorcycle-icon').classList.remove("is-active");
                document.getElementById('car-icon').classList.remove("is-active");
                selectType = $('#id_type').find(":selected").text().toLowerCase().replace('motorbike','motorcycle');
                id = selectType + '-icon';
            	document.getElementById(id).classList.add("is-active");

            });

            //        $.ajax({
            //     type: "GET",
            //     url: "/api/vehicle/",
            //     contentType: "application/json",
            //     success: function (e) {
            //         console.log(e);
            //     },
            //     error: function () {
            //
            //     }
            // });
        },

    }
})

