<template>
    <el-card shadow='hover' class='mb-2'>
        <template #header>
            <div class='card-header flex justify-between items-center'>
                <div>&nbsp;</div>
                <div>
                    <el-link type='primary' :underline='false' href='javascript:;' @click='loadStocks'>
                        刷新</el-link>
                    <el-link type='primary' :underline='false' href='javascript:;' @click='addNewStock'>
                        添加</el-link>
                </div>
            </div>
        </template>
        <el-table :data='stocks' border style='width: 100%;'>
            <el-table-column type='index' label='序号' width='50' />
            <el-table-column prop='name' label='名称' width='100'>
                <template #default='scope'>
                    <el-link
                        type='primary'
                        :underline='false'
                        :href='`https://stockpage.10jqka.com.cn/${scope.row.code}`'
                        target='_blank'
                    >{{ scope.row.name
                    }}</el-link>
                </template>
            </el-table-column>
            <el-table-column prop='code' label='代码' sortable width='80' />
            <el-table-column prop='watch_status' label='状态' width='100' sortable />
            <el-table-column prop='strategy' label='策略' width='80' />
            <el-table-column label='区间涨幅' width='220'>
                <template #default='scope'>
                    <el-popover placement='right-end' :width='500' trigger='hover'>
                        <template #reference>
                            <div>
                                <span v-for='item in scope.row.daily_data' :key='item.trade_date'>
                                    <span :class='addClass(item.daily_change)'>{{ item.daily_change }}%</span>,&nbsp;&nbsp;
                                </span>
                            </div>
                        </template>
                        <!-- popover 内容 -->
                        <el-table :data='scope.row.daily_data' style='width: 100%'>
                            <el-table-column prop='trade_date' label='日期' width='150' />
                            <el-table-column prop='daily_change' label='涨幅' width='100'>
                                <template #default='{ row }'>
                                    <span :class='addClass(row.daily_change)'>{{ row.daily_change }}%</span>
                                </template>
                            </el-table-column>
                            <el-table-column prop='max_daily_change' label='最大涨幅' width='100'>
                                <template #default='{ row }'>
                                    <span :class='addClass(row.max_daily_change)'>{{ row.max_daily_change }}%</span>
                                </template>
                            </el-table-column>
                            <el-table-column prop='min_daily_change' label='最低涨幅' width='100'>
                                <template #default='{ row }'>
                                    <span :class='addClass(row.min_daily_change)'>{{ row.min_daily_change }}%</span>
                                </template>
                            </el-table-column>
                        </el-table>
                    </el-popover>
                </template>
            </el-table-column>
            <el-table-column label='最大涨幅' width='220'>
                <template #default='scope'>
                    <el-popover placement='right-end' :width='500' trigger='hover'>
                        <template #reference>
                            <div>
                                <span v-for='item in scope.row.daily_data' :key='item.trade_date'>
                                    <span :class='addClass(item.max_daily_change)'>{{ item.max_daily_change }}%</span>,&nbsp;
                                </span>
                            </div>
                        </template>
                        <!-- popover 内容 -->
                        <el-table :data='scope.row.daily_data' style='width: 100%'>
                            <el-table-column prop='trade_date' label='日期' width='150' />
                            <el-table-column prop='max_daily_change' label='最大收益' width='100'>
                                <template #default='{ row }'>
                                    <span :class='addClass(row.max_daily_change)'>{{ row.max_daily_change }}%</span>
                                </template>
                            </el-table-column>
                            <el-table-column prop='min_daily_change' label='最低涨幅' width='100'>
                                <template #default='{ row }'>
                                    <span :class='addClass(row.min_daily_change)'>{{ row.min_daily_change }}%</span>
                                </template>
                            </el-table-column>
                        </el-table>
                    </el-popover>
                </template>
            </el-table-column>

            <el-table-column prop='total_return' label='累计涨幅' width='110' sortable>
                <template #default='scope'>
                    <span :class='addClass(scope.row.total_return)'>{{ scope.row.total_return }}%</span>
                </template>
            </el-table-column>
            <el-table-column prop='max_total_return' label='最大涨幅' width='110' sortable>
                <template #default='scope'>
                    <span :class='addClass(scope.row.max_total_return)'>{{ scope.row.max_total_return }}%</span>
                </template>
            </el-table-column>
            <el-table-column prop='create_time' label='监听日期' width='160' sortable />
            <el-table-column prop='end_time' label='结束日期' width='160' sortable />
            <el-table-column fixed='right' label='操作' width='240'>
                <template #default='scope'>
                    <el-button
                        v-if='scope.row.watch_status === "监听中"'
                        type='text'
                        size='small'
                        @click='onUpdateWatchStockBuyMonitor(scope.row)'
                    >
                        {{ scope.row.is_buy_monitor ? '停止买点监听' : '买点监听' }}
                    </el-button>
                    <el-button
                        v-if='scope.row.watch_status !== "监听中"'
                        type='text'
                        size='small'
                        @click='handleUpdateWatchStockStatus(scope.row.id, "监听中")'
                    >继续监听</el-button>
                    <el-button
                        v-if='scope.row.watch_status === "监听中"'
                        type='text'
                        size='small'
                        @click='handleUpdateWatchStockStatus(scope.row.id, "停止监听")'
                    >停止监听</el-button>
                    <el-button
                        v-if='scope.row.watch_status === "监听中" || scope.row.watch_status === "停止监听"'
                        type='text'
                        size='small'
                        @click='handleUpdateWatchStockStatus(scope.row.id, "结束监听")'
                    >结束监听</el-button>
                </template>
            </el-table-column>
        </el-table>
    </el-card>

    <el-dialog v-model='show' title='新增监听股票' width='30%' :before-close='handleClose'>
        <el-form ref='ruleForm' label-position='right' label-width='80px' :rules='rules'>
            <el-form-item class='mb-6 -ml-20' prop='code'>
                <el-input
                    v-model='newStock'
                    maxlength='6'
                    minlength='6'
                    placeholder='请输入股票代码'
                    prefix-icon='el-icon-user'
                />
            </el-form-item>
        </el-form>
        <template #footer>
            <span class='dialog-footer'>
                <el-button @click='show = false'>取消</el-button>
                <el-button type='primary' @click='addWatchStock'>添加</el-button>
            </span>
        </template>
    </el-dialog>

    <!-- <el-card shadow='hover' class='mb-2'>
        <template #header>
            <div class='card-header flex justify-between items-center'>
                <span>预警</span>
            </div>
        </template>
        <list :data='list'>
            <template #default='scope'>
                <el-button @click='edit(scope.item)'>查看</el-button>
            </template>
        </list>
    </el-card> -->
</template>
<script setup lang="ts">
import { onMounted, onUnmounted, reactive, ref, defineProps, watchEffect } from 'vue'
import { addWatchStockApi, getWatchStocksApi, removeWatchStock, updateWatchStockStatus, updateWatchStockBuyMonitorApi } from '/@/api/layout/index'
import { ElNotification, ElMessageBox, ElMessage, ElTable } from 'element-plus'


// 接收prop:type
const props = defineProps<{
    type: string
}>()


// 响应式状态声明
const rules = reactive({
    code: [
        {
            required: true,
            message: '请输入股票代码',
            trigger: 'blur'
        },
        {
            min: 6,
            max: 6,
            message: '股票代码为6位',
            trigger: 'blur'
        }
    ]
})


const stocks = ref<IStocks[]>([])
const newStock = ref<string>('')
const show = ref(false)



// 方法定义
const loadStocks = async() => {
    const res = await getWatchStocksApi({ watch_status: props.type })
    stocks.value = res.data
}

const addWatchStock = async() => {
    const res = await addWatchStockApi({ code: newStock.value })
    if (res.data.data) {
        ElNotification({
            title: '提示',
            message: '添加成功'
        })
        show.value = false
        newStock.value = ''
        loadStocks()
    } else {
        ElNotification({
            title: '提示',
            message: res.data.message
        })
    }
}

const remove = async(code: string) => {
    ElMessageBox.confirm(
        `确认删除关注股票${code}`,
        'Warning',
        {
            confirmButtonText: 'OK',
            cancelButtonText: 'Cancel',
            type: 'warning'
        }
    )
        .then(async() => {
            const res = await removeWatchStock(code)
            if (res.data.data) {
                ElMessage({
                    type: 'success',
                    message: 'Delete completed'
                })
                loadStocks()
            } else {
                ElNotification({
                    title: '提示',
                    message: '删除失败'
                })
            }
        })
        .catch(() => {
            ElMessage({
                type: 'info',
                message: 'Delete canceled'
            })
        })
}

const handleUpdateWatchStockStatus = async(id: string, status: string) => {
    await updateWatchStockStatus({ id, status })
    await loadStocks()
}

const onUpdateWatchStockBuyMonitor = async(row: any) => {
    await updateWatchStockBuyMonitorApi({ id: row.id, is_buy_monitor: Number(!row.is_buy_monitor) })
    await loadStocks()
}

const addNewStock = () => {
    show.value = true
}

const addClass = (value: number) => {
    if (value === 0) {
        return 'cell-gray'
    }
    return value > 0 ? 'cell-red' : 'cell-green'
}

const handleClose = () => {
    show.value = false
}
// 生命周期钩
let autoReloadTimer: any = null

onMounted(() => {
    loadStocks()
    // autoReloadTimer = window.setInterval(loadStocks, 5000)
})

onUnmounted(() => {
    clearInterval(autoReloadTimer)
})
// 监听props:type
watchEffect(() => {
    loadStocks()
})
// 暴露给模板的属性和方法
defineExpose({
    loadStocks
})
</script>

<style lang='postcss' scoped>
.cell-red {
    color: red;
}

.cell-green {
    color: green;
}

.cell-gray {
    color: gray;
}

.el-link {
    margin-right: 8px;
}

.el-link .el-icon--right.el-icon {
    vertical-align: text-bottom;
}
</style>