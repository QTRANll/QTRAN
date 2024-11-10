# Mutate Results
``` Python
{  
    "id": "ftevent-TDcK6kP2mRRiof75k5YpPXzb",  
    "created_at": 1723886483,  
    "level": "info",  
    "message": "Step 240/240: training loss=0.00, validation loss=0.00, full validation loss=0.00",  
    "object": "fine_tuning.job.event",  
    "data": {  
        "step": 240,  
        "train_loss": 3.4570693969726562e-06,  
        "valid_loss": 2.2545838967347758e-05,  
        "total_steps": 240,  
        "full_valid_loss": 0.004403916553852115,  
        "train_mean_token_accuracy": 1.0,  
        "valid_mean_token_accuracy": 1.0,  
        "full_valid_mean_token_accuracy": 0.8761806558053207  
    },  
    "type": "metrics"  
}
```

# Eval Results
## JsonMatch_pinolo_mutate_llm_postgres
1. 设置
``` JSON
mutate_llm_Args = {  
    "completion_fn": "openai/pinolo-mutate-llm-postgres",  
    "eval": "JsonMatch_pinolo_mutate_llm_postgres",  
    "cache": True,  
    "seed": 20220722  
}
```

2. metrics
``` JSON
{
   "final_report": {
     "accuracy": 0.9875, 
     "f1_score": 0.9997881355932204, 
     "boostrap_std": 0.01248176169456861
    }, 
    "run_id": "240819031454YKW2HLXY"
}

```

3. 出错项(1/80)
``` JSON
FixMCmpOpU，给出的回答漏掉了一种情况，漏掉的是correct answer的情况
{  
  "run_id": "240819031454YKW2HLXY",  
  "event_id": 96,  
  "sample_id": "JsonMatch_pinolo_mutate_llm_postgres.test.21",  
  "type": "sampling",  
  "data": {  
    "prompt": [  
      {  
        "role": "system",  
        "content": "You are an expert in PostgresSQL statement mutation.Mutate the seed SQL given by user into the mutated SQLs according to the mutate strategy \"FixMCmpOpU\": \"a {>|<|=} b -> a {>=|<=|>=} b\".This mutate strategy will mutate all Binary operation expressions and Comparison subquery expressions in the seed SQL once a time and give the positive \"flag\" of each expression (such as NOT,NOT IN,IS FALSE, <>, etc. which represent \"flag\"=False). For each Binary operation expression or Comparison subquery expression, it will change \">\" to \">=\",\"<\" to \"<=\",\"=\" to \">=\", and provide the positive \"flag\" for the expression.Organize answer in a JSON list format."      },  
      {  
        "role": "user",  
        "content": "SELECT (f6) AS f1, (f5) AS f2, (DATE_TRUNC('month', '2001-09-23'::date) - INTERVAL '1 day') AS f3 FROM (SELECT col_float_undef_signed AS f4, col_double_undef_signed AS f5, col_float_key_signed AS f6 FROM table_7_utf8_undef) AS t1 WHERE (NOT (SUBSTRING(f6::text FROM 1 FOR CHAR_LENGTH(f6::text)) = ANY (SELECT col_char_20_key_signed FROM table_7_utf8_undef))) OR (((EXTRACT(EPOCH FROM TIMESTAMP '2019-09-01 09:59:36')) > (EXTRACT(EPOCH FROM TIMESTAMP '1970-01-01 00:00:00') - 1)) IS TRUE)"  
      }  
    ],  
    "sampled": [  
      "[{'mutated sql': \"SELECT (f6) AS f1, (f5) AS f2, (DATE_TRUNC('month', '2001-09-23'::date) - INTERVAL '1 day') AS f3 FROM (SELECT col_float_undef_signed AS f4, col_double_undef_signed AS f5, col_float_key_signed AS f6 FROM table_7_utf8_undef) AS t1 WHERE (NOT (SUBSTRING(f6::text FROM 1 FOR CHAR_LENGTH(f6::text)) = ANY (SELECT col_char_20_key_signed FROM table_7_utf8_undef))) OR (((EXTRACT(EPOCH FROM TIMESTAMP '2019-09-01 09:59:36')) >= (EXTRACT(EPOCH FROM TIMESTAMP '1970-01-01 00:00:00') - 1)) IS TRUE)\", 'flag': True}]"  
    ],  
    "model": "ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9x9umpsR",  
    "usage": {  
      "completion_tokens": 190,  
      "prompt_tokens": 347,  
      "total_tokens": 537  
    }  
  },  
  "created_by": "zhuqinglin",  
  "created_at": "2024-08-19 03:15:15.786132+00:00"  
}  
{  
  "run_id": "240819031454YKW2HLXY",  
  "event_id": 97,  
  "sample_id": "JsonMatch_pinolo_mutate_llm_postgres.test.21",  
  "type": "match",  
  "data": {  
    "correct": false,  
    "expected": {  
      "mutated sql": "SELECT (f6) AS f1, (f5) AS f2, (DATE_TRUNC('month', '2001-09-23'::date) - INTERVAL '1 day') AS f3 FROM (SELECT col_float_undef_signed AS f4, col_double_undef_signed AS f5, col_float_key_signed AS f6 FROM table_7_utf8_undef) AS t1 WHERE (NOT (SUBSTRING(f6::text FROM 1 FOR CHAR_LENGTH(f6::text)) >= ANY (SELECT col_char_20_key_signed FROM table_7_utf8_undef))) OR (((EXTRACT(EPOCH FROM TIMESTAMP '2019-09-01 09:59:36')) > (EXTRACT(EPOCH FROM TIMESTAMP '1970-01-01 00:00:00') - 1)) IS TRUE)",  
      "flag": false  
    },  
    "picked": []  
  },  
  "created_by": "zhuqinglin",  
  "created_at": "2024-08-19 03:15:15.786132+00:00"  
}  
{  
  "run_id": "240819031454YKW2HLXY",  
  "event_id": 98,  
  "sample_id": "JsonMatch_pinolo_mutate_llm_postgres.test.21",  
  "type": "metrics",  
  "data": {  
    "accuracy": 0.0,  
    "f1_score": 0.9830508474576272  
  },  
  "created_by": "zhuqinglin",  
  "created_at": "2024-08-19 03:15:15.786132+00:00"  
}
```


## JsonMatch_basic_mutate_llm_postgres
1. 设置
``` JSON
mutate_llm_Args = {  
    "completion_fn": "openai/pinolo-mutate-llm-postgres",  
    "eval": "JsonMatch_basic_mutate_llm_postgres",  
    "cache": True,  
    "seed": 20220722  
}
```
2. metrics
``` JSON
{  
  "final_report": {  
    "accuracy": 0.9625,  
    "f1_score": 0.9898809523809525,  
    "boostrap_std": 0.021237878895972635  
  },  
  "run_id": "240819023422GQWINNCF"  
}
```

3. 出错项(3/80)

``` JSON
FixMCmpOpU，给出的回答漏掉了一种可能的变异情况（不确定），但没有漏掉correct answer的情况
{  
  "run_id": "240819023422GQWINNCF",  
  "event_id": 15,  
  "sample_id": "JsonMatch_basic_mutate_llm_postgres.test.22",  
  "type": "sampling",  
  "data": {  
    "prompt": [  
      {  
        "role": "system",  
        "content": "You are an expert in PostgresSQL statement mutation.Mutate the seed SQL given by user into the mutated SQLs according to the mutate strategy \"FixMCmpOpU\": \"a {>|<|=} b -> a {>=|<=|>=} b\".This mutate strategy will mutate all Binary operation expressions and Comparison subquery expressions in the seed SQL once a time and give the positive \"flag\" of each expression (such as NOT,NOT IN,IS FALSE, <>, etc. which represent \"flag\"=False). For each Binary operation expression or Comparison subquery expression, it will change \">\" to \">=\",\"<\" to \"<=\",\"=\" to \">=\", and provide the positive \"flag\" for the expression.Organize answer in a JSON list format."      },  
      {  
        "role": "user",  
        "content": "SELECT (f6) AS f1, (-f6) AS f2, (NOT (ATAN(0.3063398369927004) > 0)) AS f3 FROM (SELECT col_double_key_signed AS f4, col_varchar_20_key_signed AS f5, col_double_key_signed AS f6 FROM table_7_utf8_undef) AS t1 WHERE (NOT (CAST(f5 AS TEXT) ~ '[0-9]$')) OR (NOT (f4 IS DISTINCT FROM (SELECT MAX(col_double_undef_signed) FROM table_7_utf8_undef))) OR (NOT (f6::text = ANY (SELECT MAX(col_varchar_20_undef_signed) FROM table_7_utf8_undef)))"  
      }  
    ],  
    "sampled": [  
      "[{'mutated sql': \"SELECT (f6) AS f1, (-f6) AS f2, (NOT (ATAN(0.3063398369927004) > 0)) AS f3 FROM (SELECT col_double_key_signed AS f4, col_varchar_20_key_signed AS f5, col_double_key_signed AS f6 FROM table_7_utf8_undef) AS t1 WHERE (NOT (CAST(f5 AS TEXT) ~ '[0-9]$')) OR (NOT (f4 IS DISTINCT FROM (SELECT MAX(col_double_undef_signed) FROM table_7_utf8_undef))) OR (NOT (f6::text >= ANY (SELECT MAX(col_varchar_20_undef_signed) FROM table_7_utf8_undef)))\", 'flag': False}]"  
    ],  
    "model": "ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9x9umpsR",  
    "usage": {  
      "completion_tokens": 169,  
      "prompt_tokens": 325,  
      "total_tokens": 494  
    }  
  },  
  "created_by": "zhuqinglin",  
  "created_at": "2024-08-19 02:34:28.315536+00:00"  
}  
{  
  "run_id": "240819023422GQWINNCF",  
  "event_id": 16,  
  "sample_id": "JsonMatch_basic_mutate_llm_postgres.test.22",  
  "type": "match",  
  "data": {  
    "correct": false,  
    "expected": [  
      {  
        "mutated sql": "SELECT (f6) AS f1, (-f6) AS f2, (NOT (ATAN(0.3063398369927004) >= 0)) AS f3 FROM (SELECT col_double_key_signed AS f4, col_varchar_20_key_signed AS f5, col_double_key_signed AS f6 FROM table_7_utf8_undef) AS t1 WHERE (NOT (CAST(f5 AS TEXT) ~ '[0-9]$')) OR (NOT (f4 IS DISTINCT FROM (SELECT MAX(col_double_undef_signed) FROM table_7_utf8_undef))) OR (NOT (f6::text = ANY (SELECT MAX(col_varchar_20_undef_signed) FROM table_7_utf8_undef)))",  
        "flag": true  
      },  
      {  
        "mutated sql": "SELECT (f6) AS f1, (-f6) AS f2, (NOT (ATAN(0.3063398369927004) > 0)) AS f3 FROM (SELECT col_double_key_signed AS f4, col_varchar_20_key_signed AS f5, col_double_key_signed AS f6 FROM table_7_utf8_undef) AS t1 WHERE (NOT (CAST(f5 AS TEXT) ~ '[0-9]$')) OR (NOT (f4 IS DISTINCT FROM (SELECT MAX(col_double_undef_signed) FROM table_7_utf8_undef))) OR (NOT (f6::text >= ANY (SELECT MAX(col_varchar_20_undef_signed) FROM table_7_utf8_undef)))",  
        "flag": false  
      }  
    ],  
    "picked": []  
  },  
  "created_by": "zhuqinglin",  
  "created_at": "2024-08-19 02:34:28.315536+00:00"  
}  
{  
  "run_id": "240819023422GQWINNCF",  
  "event_id": 17,  
  "sample_id": "JsonMatch_basic_mutate_llm_postgres.test.22",  
  "type": "metrics",  
  "data": {  
    "accuracy": 0.0,  
    "f1_score": 0.6666666666666666  
  },  
  "created_by": "zhuqinglin",  
  "created_at": "2024-08-19 02:34:28.315536+00:00"  
}
```



``` JSON
FixMDistinctL，给出的回答漏掉了一种可能的变异情况
{  
  "run_id": "240819023422GQWINNCF",  
  "event_id": 84,  
  "sample_id": "JsonMatch_basic_mutate_llm_postgres.test.12",  
  "type": "sampling",  
  "data": {  
    "prompt": [  
      {  
        "role": "system",  
        "content": "You are an expert in PostgresSQL statement mutation.Mutate the seed SQL given by user into the mutated SQLs according to the mutate strategy \"FixMDistinctL\" :\"Distinct false -> true\".This mutate strategy will mutate all SELECT clauses in the seed SQL once a time and give the positive \"flag\" of each clause (such as NOT,NOT IN,IS FALSE, <>, etc. which represent \"flag\"=False). For each SELECT clause, it will change \"DISTINCT\" from false to true, and provide the positive \"flag\" for the clause.Organize answer in a JSON list format."      },  
      {  
        "role": "user",  
        "content": "SELECT EXTRACT(EPOCH FROM (TO_TIMESTAMP(CAST(f6 AS TEXT), 'FM99999999999999999999')) - INTERVAL '1 minute') AS f1, (CASE WHEN LEFT(f5, 1) ~ '^[0-9]$' THEN CAST(LEFT(f5, 1) AS INTEGER) * -1 ELSE NULL END) AS f2, (CAST(f6 AS INTEGER) * -1) AS f3 FROM (SELECT col_varchar_20_undef_signed AS f4, col_char_20_key_signed AS f5, col_double_undef_signed AS f6 FROM table_3_utf8_undef) AS t1 UNION SELECT (f7 * f9) AS f1, (CAST(f7 AS INTEGER)) AS f2, (f7) AS f3 FROM (SELECT col_bigint_undef_signed AS f7, col_double_key_unsigned AS f8, col_decimal_40_20_undef_signed AS f9 FROM table_7_utf8_undef) AS t2"  
      }  
    ],  
    "sampled": [  
      "[{'mutated sql': \"SELECT DISTINCT EXTRACT(EPOCH FROM (TO_TIMESTAMP(CAST(f6 AS TEXT), 'FM99999999999999999999')) - INTERVAL '1 minute') AS f1, (CASE WHEN LEFT(f5, 1) ~ '^[0-9]$' THEN CAST(LEFT(f5, 1) AS INTEGER) * -1 ELSE NULL END) AS f2, (CAST(f6 AS INTEGER) * -1) AS f3 FROM (SELECT col_varchar_20_undef_signed AS f4, col_char_20_key_signed AS f5, col_double_undef_signed AS f6 FROM table_3_utf8_undef) AS t1 UNION SELECT (f7 * f9) AS f1, (CAST(f7 AS INTEGER)) AS f2, (f7) AS f3 FROM (SELECT col_bigint_undef_signed AS f7, col_double_key_unsigned AS f8, col_decimal_40_20_undef_signed AS f9 FROM table_7_utf8_undef) AS t2\", 'flag': True}, {'mutated sql': \"SELECT EXTRACT(EPOCH FROM (TO_TIMESTAMP(CAST(f6 AS TEXT), 'FM99999999999999999999')) - INTERVAL '1 minute') AS f1, (CASE WHEN LEFT(f5, 1) ~ '^[0-9]$' THEN CAST(LEFT(f5, 1) AS INTEGER) * -1 ELSE NULL END) AS f2, (CAST(f6 AS INTEGER) * -1) AS f3 FROM (SELECT DISTINCT col_varchar_20_undef_signed AS f4, col_char_20_key_signed AS f5, col_double_undef_signed AS f6 FROM table_3_utf8_undef) AS t1 UNION SELECT (f7 * f9) AS f1, (CAST(f7 AS INTEGER)) AS f2, (f7) AS f3 FROM (SELECT col_bigint_undef_signed AS f7, col_double_key_unsigned AS f8, col_decimal_40_20_undef_signed AS f9 FROM table_7_utf8_undef) AS t2\", 'flag': True}, {'mutated sql': \"SELECT EXTRACT(EPOCH FROM (TO_TIMESTAMP(CAST(f6 AS TEXT), 'FM99999999999999999999')) - INTERVAL '1 minute') AS f1, (CASE WHEN LEFT(f5, 1) ~ '^[0-9]$' THEN CAST(LEFT(f5, 1) AS INTEGER) * -1 ELSE NULL END) AS f2, (CAST(f6 AS INTEGER) * -1) AS f3 FROM (SELECT col_varchar_20_undef_signed AS f4, col_char_20_key_signed AS f5, col_double_undef_signed AS f6 FROM table_3_utf8_undef) AS t1 UNION SELECT DISTINCT (f7 * f9) AS f1, (CAST(f7 AS INTEGER)) AS f2, (f7) AS f3 FROM (SELECT col_bigint_undef_signed AS f7, col_double_key_unsigned AS f8, col_decimal_40_20_undef_signed AS f9 FROM table_7_utf8_undef) AS t2\", 'flag': True}]"  
    ],  
    "model": "ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9x9umpsR",  
    "usage": {  
      "completion_tokens": 685,  
      "prompt_tokens": 352,  
      "total_tokens": 1037  
    }  
  },  
  "created_by": "zhuqinglin",  
  "created_at": "2024-08-19 02:34:42.792323+00:00"  
}  
{  
  "run_id": "240819023422GQWINNCF",  
  "event_id": 85,  
  "sample_id": "JsonMatch_basic_mutate_llm_postgres.test.12",  
  "type": "match",  
  "data": {  
    "correct": false,  
    "expected": [  
      {  
        "mutated sql": "SELECT DISTINCT EXTRACT(EPOCH FROM (TO_TIMESTAMP(CAST(f6 AS TEXT), 'FM99999999999999999999')) - INTERVAL '1 minute') AS f1, (CASE WHEN LEFT(f5, 1) ~ '^[0-9]$' THEN CAST(LEFT(f5, 1) AS INTEGER) * -1 ELSE NULL END) AS f2, (CAST(f6 AS INTEGER) * -1) AS f3 FROM (SELECT col_varchar_20_undef_signed AS f4, col_char_20_key_signed AS f5, col_double_undef_signed AS f6 FROM table_3_utf8_undef) AS t1 UNION SELECT (f7 * f9) AS f1, (CAST(f7 AS INTEGER)) AS f2, (f7) AS f3 FROM (SELECT col_bigint_undef_signed AS f7, col_double_key_unsigned AS f8, col_decimal_40_20_undef_signed AS f9 FROM table_7_utf8_undef) AS t2",  
        "flag": true  
      },  
      {  
        "mutated sql": "SELECT EXTRACT(EPOCH FROM (TO_TIMESTAMP(CAST(f6 AS TEXT), 'FM99999999999999999999')) - INTERVAL '1 minute') AS f1, (CASE WHEN LEFT(f5, 1) ~ '^[0-9]$' THEN CAST(LEFT(f5, 1) AS INTEGER) * -1 ELSE NULL END) AS f2, (CAST(f6 AS INTEGER) * -1) AS f3 FROM (SELECT DISTINCT col_varchar_20_undef_signed AS f4, col_char_20_key_signed AS f5, col_double_undef_signed AS f6 FROM table_3_utf8_undef) AS t1 UNION SELECT (f7 * f9) AS f1, (CAST(f7 AS INTEGER)) AS f2, (f7) AS f3 FROM (SELECT col_bigint_undef_signed AS f7, col_double_key_unsigned AS f8, col_decimal_40_20_undef_signed AS f9 FROM table_7_utf8_undef) AS t2",  
        "flag": true  
      },  
      {  
        "mutated sql": "SELECT EXTRACT(EPOCH FROM (TO_TIMESTAMP(CAST(f6 AS TEXT), 'FM99999999999999999999')) - INTERVAL '1 minute') AS f1, (CASE WHEN LEFT(f5, 1) ~ '^[0-9]$' THEN CAST(LEFT(f5, 1) AS INTEGER) * -1 ELSE NULL END) AS f2, (CAST(f6 AS INTEGER) * -1) AS f3 FROM (SELECT col_varchar_20_undef_signed AS f4, col_char_20_key_signed AS f5, col_double_undef_signed AS f6 FROM table_3_utf8_undef) AS t1 UNION SELECT DISTINCT (f7 * f9) AS f1, (CAST(f7 AS INTEGER)) AS f2, (f7) AS f3 FROM (SELECT col_bigint_undef_signed AS f7, col_double_key_unsigned AS f8, col_decimal_40_20_undef_signed AS f9 FROM table_7_utf8_undef) AS t2",  
        "flag": true  
      },  
      {  
        "mutated sql": "SELECT EXTRACT(EPOCH FROM (TO_TIMESTAMP(CAST(f6 AS TEXT), 'FM99999999999999999999')) - INTERVAL '1 minute') AS f1, (CASE WHEN LEFT(f5, 1) ~ '^[0-9]$' THEN CAST(LEFT(f5, 1) AS INTEGER) * -1 ELSE NULL END) AS f2, (CAST(f6 AS INTEGER) * -1) AS f3 FROM (SELECT col_varchar_20_undef_signed AS f4, col_char_20_key_signed AS f5, col_double_undef_signed AS f6 FROM table_3_utf8_undef) AS t1 UNION SELECT (f7 * f9) AS f1, (CAST(f7 AS INTEGER)) AS f2, (f7) AS f3 FROM (SELECT DISTINCT col_bigint_undef_signed AS f7, col_double_key_unsigned AS f8, col_decimal_40_20_undef_signed AS f9 FROM table_7_utf8_undef) AS t2",  
        "flag": true  
      }  
    ],  
    "picked": []  
  },  
  "created_by": "zhuqinglin",  
  "created_at": "2024-08-19 02:34:42.792323+00:00"  
}  
{  
  "run_id": "240819023422GQWINNCF",  
  "event_id": 86,  
  "sample_id": "JsonMatch_basic_mutate_llm_postgres.test.12",  
  "type": "metrics",  
  "data": {  
    "accuracy": 0.0,  
    "f1_score": 0.8571428571428571  
  },  
  "created_by": "zhuqinglin",  
  "created_at": "2024-08-19 02:34:42.792323+00:00"  
}
```



``` JSON
FixMCmpOpU，给出的回答漏掉了一种可能的变异情况（不确定），漏掉了correct answer的情况

{  
  "run_id": "240819023422GQWINNCF",  
  "event_id": 96,  
  "sample_id": "JsonMatch_basic_mutate_llm_postgres.test.21",  
  "type": "sampling",  
  "data": {  
    "prompt": [  
      {  
        "role": "system",  
        "content": "You are an expert in PostgresSQL statement mutation.Mutate the seed SQL given by user into the mutated SQLs according to the mutate strategy \"FixMCmpOpU\": \"a {>|<|=} b -> a {>=|<=|>=} b\".This mutate strategy will mutate all Binary operation expressions and Comparison subquery expressions in the seed SQL once a time and give the positive \"flag\" of each expression (such as NOT,NOT IN,IS FALSE, <>, etc. which represent \"flag\"=False). For each Binary operation expression or Comparison subquery expression, it will change \">\" to \">=\",\"<\" to \"<=\",\"=\" to \">=\", and provide the positive \"flag\" for the expression.Organize answer in a JSON list format."      },  
      {  
        "role": "user",  
        "content": "SELECT (f6) AS f1, (f5) AS f2, (DATE_TRUNC('month', '2001-09-23'::date) - INTERVAL '1 day') AS f3 FROM (SELECT col_float_undef_signed AS f4, col_double_undef_signed AS f5, col_float_key_signed AS f6 FROM table_7_utf8_undef) AS t1 WHERE (NOT (SUBSTRING(f6::text FROM 1 FOR CHAR_LENGTH(f6::text)) = ANY (SELECT col_char_20_key_signed FROM table_7_utf8_undef))) OR (((EXTRACT(EPOCH FROM TIMESTAMP '2019-09-01 09:59:36')) > (EXTRACT(EPOCH FROM TIMESTAMP '1970-01-01 00:00:00') - 1)) IS TRUE)"  
      }  
    ],  
    "sampled": [  
      "[{'mutated sql': \"SELECT (f6) AS f1, (f5) AS f2, (DATE_TRUNC('month', '2001-09-23'::date) - INTERVAL '1 day') AS f3 FROM (SELECT col_float_undef_signed AS f4, col_double_undef_signed AS f5, col_float_key_signed AS f6 FROM table_7_utf8_undef) AS t1 WHERE (NOT (SUBSTRING(f6::text FROM 1 FOR CHAR_LENGTH(f6::text)) = ANY (SELECT col_char_20_key_signed FROM table_7_utf8_undef))) OR (((EXTRACT(EPOCH FROM TIMESTAMP '2019-09-01 09:59:36')) >= (EXTRACT(EPOCH FROM TIMESTAMP '1970-01-01 00:00:00') - 1)) IS TRUE)\", 'flag': True}]"  
    ],  
    "model": "ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9x9umpsR",  
    "usage": {  
      "completion_tokens": 190,  
      "prompt_tokens": 347,  
      "total_tokens": 537  
    }  
  },  
  "created_by": "zhuqinglin",  
  "created_at": "2024-08-19 02:34:44.369236+00:00"  
}  
{  
  "run_id": "240819023422GQWINNCF",  
  "event_id": 97,  
  "sample_id": "JsonMatch_basic_mutate_llm_postgres.test.21",  
  "type": "match",  
  "data": {  
    "correct": false,  
    "expected": [  
      {  
        "mutated sql": "SELECT (f6) AS f1, (f5) AS f2, (DATE_TRUNC('month', '2001-09-23'::date) - INTERVAL '1 day') AS f3 FROM (SELECT col_float_undef_signed AS f4, col_double_undef_signed AS f5, col_float_key_signed AS f6 FROM table_7_utf8_undef) AS t1 WHERE (NOT (SUBSTRING(f6::text FROM 1 FOR CHAR_LENGTH(f6::text)) >= ANY (SELECT col_char_20_key_signed FROM table_7_utf8_undef))) OR (((EXTRACT(EPOCH FROM TIMESTAMP '2019-09-01 09:59:36')) > (EXTRACT(EPOCH FROM TIMESTAMP '1970-01-01 00:00:00') - 1)) IS TRUE)",  
        "flag": false  
      },  
      {  
        "mutated sql": "SELECT (f6) AS f1, (f5) AS f2, (DATE_TRUNC('month', '2001-09-23'::date) - INTERVAL '1 day') AS f3 FROM (SELECT col_float_undef_signed AS f4, col_double_undef_signed AS f5, col_float_key_signed AS f6 FROM table_7_utf8_undef) AS t1 WHERE (NOT (SUBSTRING(f6::text FROM 1 FOR CHAR_LENGTH(f6::text)) = ANY (SELECT col_char_20_key_signed FROM table_7_utf8_undef))) OR (((EXTRACT(EPOCH FROM TIMESTAMP '2019-09-01 09:59:36')) >= (EXTRACT(EPOCH FROM TIMESTAMP '1970-01-01 00:00:00') - 1)) IS TRUE)",  
        "flag": true  
      }  
    ],  
    "picked": []  
  },  
  "created_by": "zhuqinglin",  
  "created_at": "2024-08-19 02:34:44.369236+00:00"  
}  
{  
  "run_id": "240819023422GQWINNCF",  
  "event_id": 98,  
  "sample_id": "JsonMatch_basic_mutate_llm_postgres.test.21",  
  "type": "metrics",  
  "data": {  
    "accuracy": 0.0,  
    "f1_score": 0.6666666666666666  
  },  
  "created_by": "zhuqinglin",  
  "created_at": "2024-08-19 02:34:44.369236+00:00"  
}

```


## JsonMatch_pinolo_gpt-4o-mini_fewshot_postgres
1. 设置
``` JSON 
gpt_4o_mini_fewshot_Args = {  
    "completion_fn": "gpt-4o-mini",  
    "eval": "JsonMatch_pinolo_gpt-4o-mini_fewshot_postgres",  
    "cache": True,  
    "seed": 20220722  
}
```
2. metrics
``` JSON
{  
  "final_report": {  
    "accuracy": 0.125,  
    "f1_score": 0.8468648800969358,  
    "boostrap_std": 0.0371381794788059  
  },  
  "run_id": "240818184243V2U3SX4C"  
}
```



## JsonMatch_pinolo_mutate_llm_mysql
1. 设置
``` JSON
mutate_llm_Args = {  
    "completion_fn": "openai/pinolo-mutate-llm-postgres",  
    "eval": "JsonMatch_pinolo_mutate_llm_mysql",  
    "cache": True,  
    "seed": 20220722  
}
```

2. metrics
``` JSON
{  
  "final_report": {  
    "accuracy": 0.0,  
    "f1_score": 0.8465055105422851,  
    "boostrap_std": 0.0  
  },  
  "run_id": "240823040156ZSLSCPYY"  
}
```

3. 出错
* mutate llm输出的结果不符合json格式要求，只得出了mutated sql而没有flag。推断原因是：mysql的测试数据中的role prompt和postgres中的不同，且user message是mysql语法的。
```
Mutated SQLs:

1. SELECT DISTINCT (-`f14`) AS `f1`,(TRIM(`f15`)) AS `f2`,(`f15`) AS `f3` FROM (SELECT (`f17`) AS `f13`,('i'*CHARSET(`f19`)) AS `f16`,(-`f19`) AS `f15` FROM (SELECT `col_char(20)_undef_signed` AS `f17`,`col_double_undef_signed` AS `f18`,`col_float_key_unsigned` AS `f19` FROM `table_7_utf8_undef`) AS `t4`) AS `t5` STRAIGHT_JOIN (SELECT `col_double_key_signed` AS `f20`,`col_decimal(40, 20)_undef_signed` AS `f14`,`col_decimal(40, 20)_key_unsigned` AS `f21` FROM `table_3_utf8_undef`) AS `t6`  flag=True

2. SELECT (-`f14`) AS `f1`,(TRIM(`f15`)) AS `f2`,(`f15`) AS `f3` FROM (SELECT DISTINCT (`f17`) AS `f13`,('i'*CHARSET(`f19`)) AS `f16`,(-`f19`) AS `f15` FROM (SELECT `col_char(20)_undef_signed` AS `f17`,`col_double_undef_signed` AS `f18`,`col_float_key_unsigned` AS `f19` FROM `table_7_utf8_undef`) AS `t4`) AS `t5` STRAIGHT_JOIN (SELECT `col_double_key_signed` AS `f20`,`col_decimal(40, 20)_undef_signed` AS `f14`,`col_decimal(40, 20)_key_unsigned` AS `f21` FROM `table_3_utf8_undef`) AS `t6`  flag=True

3. SELECT (-`f14`) AS `f1`,(TRIM(`f15`)) AS `f2`,(`f15`) AS `f3` FROM (SELECT (`f17`) AS `f13`,('i'*CHARSET(`f19`)) AS `f16`,(-`f19`) AS `f15` FROM (SELECT DISTINCT `col_char(20)_undef_signed` AS `f17`,`col_double_undef_signed` AS `f18`,`col_float_key_unsigned` AS `f19` FROM `table_7_utf8_undef`) AS `t4`) AS `t5` STRAIGHT_JOIN (SELECT `col_double_key_signed` AS `f20`,`col_decimal(40, 20)_undef_signed` AS `f14`,`col_decimal(40, 20)_key_unsigned` AS `f21` FROM `table_3_utf8_undef`) AS `t6`  flag=True

4. SELECT (-`f14`) AS `f1`,(TRIM(`f15`)) AS `f2`,(`f15`) AS `f3` FROM (SELECT (`f17`) AS `f13`,('i'*CHARSET(`f19`)) AS `f16`,(-`f19`) AS `f15` FROM (SELECT `col_char(20)_undef_signed` AS `f17`,`col_double_undef_signed` AS `f18`,`col_float_key_unsigned` AS `f19` FROM `table_7_utf8_undef`) AS `t4`) AS `t5` STRAIGHT_JOIN (SELECT DISTINCT `col_double_key_signed` AS `f20`,`col_decimal(40, 20)_undef_signed` AS `f14`,`col_decimal(40, 20)_key_unsigned` AS `f21` FROM `table_3_utf8_undef`) AS `t6`  flag=True

```
* 对于不同的db：需要添加特定的mutate strategies描述（不同db之间有细微差距）以及对应的训练数据（不同db的训练sql）




