<template>
    <div class='content'>
        <el-row :gutter='15'>
            <el-col :md='24' :lg='24'>
                <!-- <Position /> -->
                <el-button-group>
                    <el-button type='primary' @click="onChangeListType('监听中')">监听中股票</el-button>
                    <el-button type='primary' @click="onChangeListType('结束监听')">结束监听</el-button>
                    <el-button type='primary' @click="onChangeListType('停止监听')">停止监听</el-button>
                    <el-button type='primary' @click="onChangeListType(null)">全部股票</el-button>
                </el-button-group>
                <List :type='listType' />
            </el-col>
        </el-row>
    </div>
</template>

<script setup lang='ts'>
import { ref } from 'vue'
import { useLayoutStore } from '/@/store/modules/layout'
import List from '/@/views/Dashboard/Workplace/_Components/List.vue'

// 获取用户信息
const { getUserInfo } = useLayoutStore()

// 定义响应式变量
const listType = ref('监听中')

// 定义方法
const onChangeListType = (type: string) => {
    listType.value = type
}

</script>