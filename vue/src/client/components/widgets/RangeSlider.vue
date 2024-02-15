<template>
    <div class="range-slider">
        <span class="line"></span>
        <span ref="fillLine" class="fill-line"></span>
        <ul>
            <li v-for="value in values" :key="value" @click="makeItemActive">
                {{ value.title }}
            </li>
        </ul>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const emits = defineEmits(["update:option"]);
const fillLine = ref(null);

function makeItemActive(event) {
    fillLine.value.style.visibility = "visible"
    const childrens = [...event.target.parentElement.children];
    var child;

    for (child of childrens) {
        child.classList.remove("active");
    }
    const obj = values.find((item) => item.title === event.target.innerHTML);
    fillLine.value.style.width = obj.amount + "%";

    let i = 0;
    for (child of childrens.reverse()) {
        child.classList.add("active");
        console.log(i)
        if (i === obj.amount) {
            break
        } else {
            i += 25;
        }
    }

    event.target.classList.add("active");
    emits("update:option", obj.amount);
}

const values = [
    {
        title: "100%",
        amount: 100,
    },
    {
        title: "75%",
        amount: 75,
    },
    {
        title: "50%",
        amount: 50,
    },
    {
        title: "25%",
        amount: 25,
    },
    {
        title: "0%",
        amount: 0,
    },
];

onMounted(() => {
    fillLine.value.style.visibility = "hidden"
})
</script>

<style scoped>
div {
    position: relative;
}

ul {
    display: flex;
    justify-content: space-between;
    direction: rtl;
    position: relative;
    top: 10px;
}

ul>li::after {
    content: "";
    position: absolute;
    width: 10px;
    height: 10px;
    background: #698796;
    border-radius: 100%;
    bottom: 26px;
    z-index: 99;
    margin-right: -20px;
}

ul>li:first-child::after {
    right: 0;
    margin-right: 0;
}

ul>li:last-child::after {
    left: 0px;
}

span.line {
    position: absolute;
    width: 100%;
    height: 3px;
    background: #698796;
    padding: 0;
}

span.fill-line {
    position: absolute;
    width: 50%;
    height: 3px;
    background: #ffd60a;
    padding: 0;
    left: 0;
    z-index: 999;
}

.active::after {
    background: #ffd60a;
}

body[data-theme="light"] span.line {
    background: #d8e5ea;
}

body[data-theme="light"] ul>li::after {
    background: #d8e5ea;
}

body[data-theme="light"] .active::after {
    background: #ffd60a;
}
</style>
