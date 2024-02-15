<!-- Generate vue component with input range. It shoul input values from props min default 0 to props max default 100 with step as props step default 1. There should be props labels which is array of objects with fields: label and value. Label should be li component placed under input range at position according to value field and text from label field. When user press on label input vlue shold became an value of label. When value in input and value in label equals, label text should colorized red. --><template>
    <div>
        <input type="range" v-model="inputValue" :min="min" :max="max" :step="step" @input="handleInput" />
        <ul>
            <li v-for="label in labels" :key="label.value" :style="{ left: calculatePosition(label.value) + '%' }" @click="handleLabelClick(label)">
                {{ label.label }}
            </li>
        </ul>
    </div>
</template>

<script>
export default {
    name: "SliderWidget",
    props: {
        min: {
            type: Number,
            default: 0
        },
        max: {
            type: Number,
            default: 100
        },
        step: {
            type: Number,
            default: 1
        },
        labels: {
            type: Array,
            default: () => [
                {
                    label: "0",
                    value: 0
                },
                {
                    label: "25",
                    value: 25
                },
                {
                    label: "50",
                    value: 50
                },
                {
                    label: "75",
                    value: 75
                },
                {
                    label: "100",
                    value: 100
                }
            ]
        }
    },
    data() {
        return {
            inputValue: 0
        };
    },
    methods: {
        handleInput() {
            // Handle input change
        },
        handleLabelClick() {
            // Handle label click
        },
        calculatePosition() {
            // Calculate position based on value
        }
    }
};
</script>
