import Vue from 'vue'
import Vuex from 'vuex'
import {isNotNullORBlank} from "../common/utils";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
      routes: [],
      sessions: {},
      report_component_display:true,
      currentSession: null,
      // isNotNullORBlank(window.localStorage.getItem('user' || '[]') ) ? JSON.parse(window.localStorage.getItem('user' || '[]')).user.realName : '未登录' ,
      currentHr: isNotNullORBlank(window.sessionStorage.getItem("user")) ? JSON.parse(window.sessionStorage.getItem("user")) : '',
      detect_record_list: [],
      current_record_id:0,
      current_group_id:0,
  },
  mutations: {
      init_routes(state, data) {
          state.routes = data;
      },
      init_currentUser(state, hr) {
          state.currentHr = hr;
      },
      init_detect_record_list(state,detect_record_list){
          state.detect_record_list = detect_record_list;
      },
      init_current_record_id(state,record_id){
          state.current_record_id = record_id;
      },
      init_current_group_id(state,group_id){
          state.current_group_id = group_id;
      },
      set_report_component_display(state,report_component_display){
          state.report_component_display =report_component_display

      },
      add_detect_record_to_detect_record_list(state,detect_record){
          state.detect_record_list[state.detect_record_list.length] = detect_record
      }

  },
  actions: {
  },
  modules: {
  }
})
