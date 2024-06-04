0000000000401130 <main>:
  401130:	cmp    $0x4,%edi
  401133:	jl     401183
  401150:	add    $0x1,%esi
  401153:	mov    %edi,%eax
  401155:	cltd   
  401156:	idiv   %esi
  401158:	test   %edx,%edx
  40115a:	je     401169
  40115c:	cmp    %ecx,%esi
  40115e:	jl     401150
  401169:	mov    $0x1,%al
  40116b:	cmp    $0x1,%edi
  40116e:	je     401183
  401170:	test   %al,%al
  401172:	jne    401183
  401174:	push   %rax
  401175:	callq  401110
  40117a:	mov    %eax,%edi
  40117c:	add    $0x8,%rsp
  401180:	mov    %edi,%eax
  401182:	retq   
  401183:	mov    %edi,%eax
  401185:	retq   
