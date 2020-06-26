/* 是否手机号码*/
export function validatePhone(rule, value,callback) {
  const reg =/^[1][3,4,5,7,8][0-9]{9}$/;
  console.log("telValidate");
  if(value==''||value==undefined||value==null){
    callback("请输入手机号");
  }else {
    if ((!reg.test(value)) && value != '') {
      callback(new Error('请输入正确的手机号码'));
    } else {
      callback();
    }
  }
}
/* 是否邮箱*/
export function validateMail(rule, value,callback){
  const reg =/^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/;
  if(value===''||value===null||value===undefined){
    return callback(new Error('请输入邮箱地址'));
  }else{
    if (!reg.test(value)){
      return callback(new Error('请输入正确的邮箱地址'));
    } else {
      return callback(new Error('uyhttgt'));
    }
  }
}

/*验证内容是否英文数字以及下划线*/
export function isEngNumLine(rule, value, callback) {
  const reg =/^[_a-zA-Z0-9]+$/;
  if(value==''||value==undefined||value==null){
    callback();
  } else {
    if (!reg.test(value)){
      callback(new Error('仅由英文字母/数字/下划线组成'));
    } else {
      callback();
    }
  }
}

export function isNum(rule,value,callback){

}
