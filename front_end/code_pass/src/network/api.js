import axios from 'axios'
import {Message} from 'element-ui'

//设置axios默认的超时时间
axios.defaults.timeout = 60 * 60 * 1000; // 1个小时
/**保证session的一致性**/
axios.defaults.withCredentials=true;
/**
 * 封装每一次的请求
 */
/**异步请求的拦截器**/
axios.interceptors.request.use(config => {
  // console.log(config)
  return config;
}, err => {
  Message.error({message: '请求超时!'});
  // return Promise.resolve(err);
});
/**异步响应的拦截器**/
axios.interceptors.response.use(data => {

  if (data.status && data.status === 200 && data.data.status === 500) {
    Message.error({message: data.data.msg});
    return;
  }
  if (data.data.msg) {
    Message.success({message: data.data.msg});
  }
  return data;
}, err => {

  if (err.response.status === 504 || err.response.status === 404) {

    Message.error({message: '服务器被吃了⊙﹏⊙∥'});

  } else if (err.response.status === 403) {
    Message.error({message: '权限不足,请联系管理员!'});
  } else if (err.response.status === 401) {
    Message.error({message: err.response.data.msg});
  } else {
    if (err.response.data.msg) {
      Message.error({message: err.response.data.msg});
    }else{
      Message.error({message: '未知错误!'});
    }
  }
  // return Promise.resolve(err);
});
// create an axios instance

let base = '/code_pass';
export const postRequest = (url, params,isParse) => {
  if(isParse===undefined ||isParse===false ) {
      return axios({
          method: 'post',
          url: `${base}${url}`,
          data: params,
          transformRequest: [function (data) {
              let ret = '';
              for (let it in data) {
                  ret += encodeURIComponent(it) + '=' + encodeURIComponent(data[it]) + '&'
              }
              return ret
          }],

          headers: {
              'Content-Type': 'application/x-www-form-urlencoded'
          }
      });
  }else{
      return axios({
          method: 'post',
          url: `${base}${url}`,
          data: params,

          headers: {
              'Content-Type': 'application/x-www-form-urlencoded'
          }
      });
  }
};
export const uploadFileRequest = (url, params) => {
  return axios({
    method: 'post',
    url: `${base}${url}`,
    data: params,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};
export const putRequest = (url, params) => {
  return axios({
    method: 'put',
    url: `${base}${url}`,
    data: params,
    transformRequest: [function (data) {
      let ret = '';
      for (let it in data) {
        ret += encodeURIComponent(it) + '=' + encodeURIComponent(data[it]) + '&'
      }
      return ret
    }],
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  });
};
export const deleteRequest = (url) => {
  return axios({
    method: 'delete',
    url: `${base}${url}`
  });
};
export const getRequest = (url,responseType) => {
  return axios({
    method: 'get',
    responseType:responseType==null?'':responseType,
    url: `${base}${url}`
  });
};
